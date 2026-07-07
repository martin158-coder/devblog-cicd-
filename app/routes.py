from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models import blog_storage, BlogPost
from datetime import datetime

# Crear un Blueprint para organizar las rutas
# ¿Qué es un Blueprint? Es una forma de organizar rutas en Flask
# Permite modularidad y reutilización de código
main = Blueprint("main", __name__)

# ================================
# RUTAS PARA PÁGINAS WEB (HTML)
# ================================


@main.route("/")
def index():
    """
    Página principal - Lista todos los posts del blog
    """
    posts = blog_storage.get_all_posts()
    return render_template(
        "index.html", posts=posts, title="DevBlog - Mi Blog Personal"
    )


@main.route("/post/<int:post_id>")
def view_post(post_id):
    """
    Vista individual de un post

    Args:
        post_id: ID del post a mostrar (viene de la URL)
    """
    post = blog_storage.get_post_by_id(post_id)

    if not post:
        # Si el post no existe, mostrar error 404
        return render_template("404.html"), 404

    return render_template("post.html", post=post, title=f"{post.title} - DevBlog")


@main.route("/create", methods=["GET", "POST"])
def create_post():
    """
    Crear nuevo post - Maneja tanto GET (mostrar formulario)
    como POST (procesar formulario)
    """

    if request.method == "GET":
        # Mostrar formulario para crear post
        return render_template("create_post.html", title="Crear Nuevo Post - DevBlog")

    elif request.method == "POST":
        # Procesar datos del formulario

        # Obtener datos del formulario HTML
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        author = request.form.get("author", "Anónimo").strip()

        # Validación de datos
        errors = []
        if not title:
            errors.append("El título es requerido")
        if not content:
            errors.append("El contenido es requerido")
        if len(title) > 200:
            errors.append("El título no puede tener más de 200 caracteres")

        # Si hay errores, mostrar formulario con errores
        if errors:
            for error in errors:
                flash(error, "error")  # Flash messages para mostrar errores
            return render_template(
                "create_post.html",
                title="Crear Nuevo Post - DevBlog",
                form_data={'title': title, 'content': content, "author": author})
        
        # Si no hay errores, crear el post
        try:
            new_post = BlogPost(
                title=title,
                content=content,
                author=author
            )
            
            created_post = blog_storage.create_post(new_post)

            flash('¡Post creado exitosamente!', 'success')
            return redirect(url_for('main.view_post', post_id=created_post.id))

        except Exception as e:
            flash(f'Error al crear el post: {str(e)}', 'error')
            return render_template(
                'create_post.html',
                title='Crear Nuevo Post - DevBlog',
                form_data={
                    'title': title,
                    'content': content,
                    'author': author
                }
            )


@main.route('/search')
def search():
        """
        Búsqueda de posts
        """
        query = request.args.get('q', '').strip()

        if query:
            results = blog_storage.search_posts(query)
            message = f'Resultados para: "{query}"' if results else f'No se encontraron resultados para: "{query}"'
        else:
            results = []
            message = 'Ingresa un término de búsqueda'

        return render_template(
                'search.html',
                posts=results,
                query=query,
                message=message,
                title=f'Búsqueda: {query}' if query else 'Búsqueda - DevBlog'
            )


# ================================
    # API REST ENDPOINTS (JSON)
# ================================

@main.route('/api/posts', methods=['GET'])
def api_get_posts():
    """
    API: Obtener todos los posts en formato JSON
    """
    posts = blog_storage.get_all_posts()  # ← Esta línea debe estar presente
    return jsonify({
        'success': True,
        'data': [post.to_dict() for post in posts],  # ← Aquí usa 'posts'
        'count': len(posts)
    })


@main.route('/api/posts', methods=['POST'])
def api_create_post():
    """API: Crear nuevo post vía JSON"""

    # Verificar que se envió JSON
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Content-Type debe ser application/json'
        }), 400

    # Intentar parsear JSON - capturar errores de JSON malformado
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({
            'success': False,
            'error': 'JSON malformado'
        }), 400

    if not data:
        return jsonify({
            'success': False,
            'error': 'No se proporcionaron datos JSON válidos'
        }), 400

    try:
        # Validar datos requeridos
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        author = data.get('author', 'API User').strip()

        if not title or not content:
            return jsonify({
                'success': False,
                'error': 'Título y contenido son requeridos'
            }), 400

        # Crear post
        new_post = BlogPost(
            title=title,
            content=content,
            author=author
        )

        created_post = blog_storage.create_post(new_post)

        return jsonify({
            'success': True,
            'data': created_post.to_dict(),
            'message': 'Post creado exitosamente'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@main.route('/api/posts/<int:post_id>', methods=['GET'])
def api_get_post(post_id):
    """
    API: Obtener un post específico por ID
    """
    post = blog_storage.get_post_by_id(post_id)

    if not post:
        return jsonify({
            'success': False,
            'error': 'Post no encontrado'
        }), 404

    return jsonify({
        'success': True,
        'data': post.to_dict()
    })


@main.route('/api/posts/<int:post_id>', methods=['PUT'])
def api_update_post(post_id):
    """
    API: Actualizar un post existente
    """
    try:
        # Verificar que se envió JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json'
            }), 400

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos JSON válidos'
            }), 400

        # Actualizar post
        updated_post = blog_storage.update_post(
            post_id,
            title=data.get('title'),
            content=data.get('content')
        )

        if not updated_post:
            return jsonify({
                'success': False,
                'error': 'Post no encontrado'
            }), 404

        return jsonify({
            'success': True,
            'data': updated_post.to_dict(),
            'message': 'Post actualizado exitosamente'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500


@main.route('/api/posts/<int:post_id>', methods=['DELETE'])
def api_delete_post(post_id):
    """
    API: Eliminar un post
    """
    success = blog_storage.delete_post(post_id)

    if not success:
        return jsonify({
            'success': False,
            'error': 'Post no encontrado'
        }), 404

    return jsonify({
        'success': True,
        'message': 'Post eliminado exitosamente'
    })


@main.route('/api/search', methods=['GET'])
def api_search_posts():
    """
    API: Buscar posts

    Parámetro:
    ?q=término_de_búsqueda
    """
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({
            'success': False,
            'error': 'Parámetro de búsqueda "q" es requerido'
        }), 400

    results = blog_storage.search_posts(query)

    return jsonify({
        'success': True,
        'data': [post.to_dict() for post in results],
        'query': query,
        'count': len(results)
    })

@main.route('/api/health') 
def api_health(): 
    """API: Health check endpoint""" 
    return jsonify({ 
        'status': 'healthy', 
        'version': '1.0.0', 
        'timestamp': datetime.now().isoformat(), 
        'tests_passing': True
    })
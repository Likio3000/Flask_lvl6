# Filename: ./flaskr/blog.py
# ----- Start of file content -----
import math
from typing import Any, Optional

from flask import (Blueprint, current_app, flash, g, redirect,
                   render_template, request, url_for)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

POSTS_PER_PAGE = 5 # Configuration for pagination

@bp.route('/')
def index() -> str:
    """
    Show all the posts, paginated, ordered by the most recent first.
    """
    db = get_db()
    page = request.args.get('page', 1, type=int) # Get page number from query param

    # Calculate total number of posts and pages
    count_result = db.execute('SELECT COUNT(id) FROM post').fetchone()
    total_posts = count_result[0] if count_result else 0
    total_pages = math.ceil(total_posts / POSTS_PER_PAGE)

    # Ensure requested page is valid
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages # Go to last page if requested page is too high

    # Calculate offset for the query
    offset = (page - 1) * POSTS_PER_PAGE

    # Fetch posts for the current page
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
        ' LIMIT ? OFFSET ?',
        (POSTS_PER_PAGE, offset)
    ).fetchall()

    current_app.logger.debug(f"Fetched posts for page {page}, offset {offset}")

    return render_template(
        'blog/index.html',
        posts=posts,
        page=page,
        total_pages=total_pages
    )


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create() -> Any:
    """
    Create a new post for the current user.
    Handles both displaying the form (GET) and processing submission (POST).
    """
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        error = None

        if not title:
            error = 'Title is required.'
        elif not body:
            error = 'Body is required.' # Added check for body

        if error is not None:
            flash(error)
            current_app.logger.warning(f"Post creation failed for user {g.user['id']}: {error}")
        else:
            db = get_db()
            try:
                cursor = db.execute(
                    'INSERT INTO post (title, body, author_id)'
                    ' VALUES (?, ?, ?)',
                    (title, body, g.user['id'])
                )
                db.commit()
                current_app.logger.info(f"Post '{title}' (ID: {cursor.lastrowid}) created by user {g.user['id']}.")
                flash('Post created successfully!', 'success') # Added success flash
                return redirect(url_for('blog.index'))
            except db.Error as e:
                db.rollback()
                current_app.logger.error(f"Database error during post creation: {e}")
                flash("An error occurred while creating the post. Please try again.", "error")


    return render_template('blog/create.html')


def get_post(id: int, check_author: bool = True) -> Any:
    """
    Get a specific post by id and its author.

    Args:
        id: The id of the post to get.
        check_author: If True, verifies that the current user is the author.

    Returns:
        The post data.

    Raises:
        NotFound (404): If the post doesn't exist.
        Forbidden (403): If check_author is True and the current user isn't the author.
    """
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        current_app.logger.warning(f"Post ID {id} not found.")
        abort(404, f"Post id {id} doesn't exist.")

    # g.user might be None if accessed by an unauthenticated user (e.g., viewing a post)
    if check_author:
        if g.user is None:
             current_app.logger.warning(f"Unauthorized attempt to access post {id} requiring author check.")
             abort(403) # Must be logged in to pass author check
        elif post['author_id'] != g.user['id']:
            current_app.logger.warning(f"User {g.user['id']} forbidden from modifying post {id} owned by user {post['author_id']}.")
            abort(403) # Logged in user is not the author

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id: int) -> Any:
    """
    Update an existing post. Requires the user to be the author.
    Handles displaying the form with existing data (GET) and processing updates (POST).
    """
    post = get_post(id) # get_post already checks author by default

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        error = None

        if not title:
            error = 'Title is required.'
        elif not body:
            error = 'Body is required.'

        if error is not None:
            flash(error)
            current_app.logger.warning(f"Post update failed for ID {id}: {error}")
        else:
            db = get_db()
            try:
                db.execute(
                    'UPDATE post SET title = ?, body = ?'
                    ' WHERE id = ?',
                    (title, body, id)
                )
                db.commit()
                current_app.logger.info(f"Post ID {id} updated by user {g.user['id']}.")
                flash('Post updated successfully!', 'success') # Added success flash
                return redirect(url_for('blog.index'))
            except db.Error as e:
                db.rollback()
                current_app.logger.error(f"Database error during post update (ID: {id}): {e}")
                flash("An error occurred while updating the post. Please try again.", "error")

    # Pass the original post data to the template for GET requests
    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id: int) -> Any:
    """
    Delete a post. Requires the user to be the author.
    """
    get_post(id) # Ensures post exists and user is the author
    db = get_db()

    try:
        db.execute('DELETE FROM post WHERE id = ?', (id,))
        db.commit()
        current_app.logger.info(f"Post ID {id} deleted by user {g.user['id']}.")
        flash('Post deleted successfully!', 'info') # Added success flash
    except db.Error as e:
        db.rollback()
        current_app.logger.error(f"Database error during post deletion (ID: {id}): {e}")
        flash("An error occurred while deleting the post. Please try again.", "error")

    return redirect(url_for('blog.index'))

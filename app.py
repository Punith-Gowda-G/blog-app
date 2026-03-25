from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import json
from urllib.request import urlopen
from urllib.error import URLError
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'blog-secret-key-2024'

DB_PATH = os.path.join(os.path.dirname(__file__), 'blog.db')
COMMENTS_API_URL = 'https://jsonplaceholder.typicode.com/comments'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_api_comments():
    """Fetch comment records from JSONPlaceholder; return empty list on failure."""
    try:
        with urlopen(COMMENTS_API_URL, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, list):
                return data
    except (URLError, TimeoutError, json.JSONDecodeError):
        return []
    return []


def ensure_comments_for_all_posts(conn):
    """Top up each post to 2-3 comments using API data, without duplicating every run."""
    api_comments = fetch_api_comments()
    post_rows = conn.execute('SELECT id FROM posts ORDER BY id').fetchall()

    inserted = 0
    for index, post in enumerate(post_rows):
        post_id = post['id']
        existing_count = conn.execute(
            'SELECT COUNT(*) FROM comments WHERE post_id = ?',
            (post_id,)
        ).fetchone()[0]

        if existing_count >= 2:
            continue

        # Add only enough comments to keep each post at 2-3 comments.
        to_add = 3 - existing_count

        # Spread API comments across posts in stable chunks.
        start = (index * 5) % len(api_comments) if api_comments else 0
        chunk = api_comments[start:start + to_add]

        # Fallback values if API is unavailable.
        fallback_comments = [
            {'name': 'Mia', 'body': 'Beautifully written. I could picture every detail while reading.'},
            {'name': 'Arjun', 'body': 'This gave me a fresh perspective. Thanks for sharing this.'},
            {'name': 'Noah', 'body': 'I tried this approach today and it genuinely helped me focus better.'}
        ]

        selected = chunk if len(chunk) == to_add else fallback_comments[:to_add]
        for item in selected:
            author = (item.get('name') or 'Anonymous').strip()[:80]
            content = (item.get('body') or '').strip()
            if not content:
                continue
            conn.execute(
                'INSERT INTO comments (post_id, author, content) VALUES (?, ?, ?)',
                (post_id, author, content)
            )
            inserted += 1

    return inserted, len(post_rows)

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            image_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author TEXT DEFAULT 'Anonymous',
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    ''')
    # Seed some sample posts if empty
    count = conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    if count == 0:
        sample_posts = [
            ('The Art of Slow Mornings', 
             "There's a certain magic in waking before the world does. The silence is different at 5am — it's not the silence of absence, but the silence of possibility.\n\nI've been experimenting with slow mornings for three months now. No phone for the first hour. No email. Just coffee, a notebook, and whatever thoughts decide to surface.\n\nWhat I've discovered is that the quality of my day is almost entirely determined by how I spend that first hour. When I rush — checking notifications, scrolling headlines — I spend the rest of the day in a reactive state, always catching up.\n\nWhen I protect that hour, I arrive at my desk feeling like I've already won something.\n\nThe ritual matters. It doesn't have to be elaborate. Mine is simple: boil water, grind beans, pour slowly. Sit. Write three pages of whatever is in my head. Read one chapter of something physical.\n\nThat's it. Forty-five minutes. But they're *mine*, and that changes everything.",
             'Lifestyle',
             'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=900&auto=format&fit=crop'),
            ('Why I Switched to Mechanical Keyboards',
             "Six months ago I would have laughed at anyone who spent $200 on a keyboard. Now I am that person, and I have thoughts.\n\nThe switch happened during a particularly frustrating week of writing. My membrane keyboard felt like typing through wet cardboard — no feedback, no joy, no tactile sense that anything was actually happening.\n\nA colleague let me try her mechanical board. The click of Cherry MX Blues was like suddenly hearing music after years of static.\n\nThe argument against mechanicals is usually the noise. And yes, Blues are loud. But there's a middle path: Brown switches give you tactile bump without the audible click. Reds are smooth and silent. The world of switches is surprisingly deep.\n\nWhat nobody tells you is how much the *sound* of typing affects your mood. A keyboard that sounds satisfying makes you *want* to write. That's worth something.\n\nI'm currently using a Keychron Q1 with Boba U4T switches. It sounds like gentle rain on a tin roof. I'm never going back.",
             'Tech',
             'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=900&auto=format&fit=crop'),
            ('Notes on Learning Portuguese in Six Months',
             "I moved to Lisbon without speaking a word of Portuguese. I want to document what actually worked — because most language learning advice is wrong.\n\nWhat doesn't work: Duolingo as your primary tool. It's fine for vocabulary, but it will never make you conversational. Neither will any app that doesn't force you to produce language under pressure.\n\nWhat works: Comprehensible input. The theory, developed by linguist Stephen Krashen, is that you acquire language when you understand messages slightly above your current level. Podcasts designed for learners, graded readers, TV shows you've already seen in English — these are your actual curriculum.\n\nThe other thing that works: embarrassment. Talk to people before you're ready. Be wrong constantly. Thank them when they correct you. Most people are incredibly kind to someone genuinely trying to learn their language.\n\nAt six months I'm somewhere between B1 and B2. I can argue about politics, describe my dreams, and complain about the metro. That feels like enough for now.",
             'Learning',
             'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=900&auto=format&fit=crop'),
        ]
        for title, content, category, image_url in sample_posts:
            conn.execute(
                'INSERT INTO posts (title, content, category, image_url) VALUES (?, ?, ?, ?)',
                (title, content, category, image_url)
            )

    ensure_comments_for_all_posts(conn)
    conn.commit()
    conn.close()


@app.route('/api/comments/import', methods=['POST'])
def import_comments_api():
    conn = get_db()
    inserted, post_count = ensure_comments_for_all_posts(conn)
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'ok',
        'api': COMMENTS_API_URL,
        'posts_checked': post_count,
        'comments_inserted': inserted
    })

@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    
    conn = get_db()
    sql = 'SELECT * FROM posts WHERE 1=1'
    params = []
    
    if query:
        sql += ' AND (title LIKE ? OR content LIKE ?)'
        params += [f'%{query}%', f'%{query}%']
    if category:
        sql += ' AND category = ?'
        params.append(category)
    
    sql += ' ORDER BY created_at DESC'
    posts = conn.execute(sql, params).fetchall()
    categories = [r[0] for r in conn.execute('SELECT DISTINCT category FROM posts ORDER BY category').fetchall()]
    conn.close()
    return render_template('index.html', posts=posts, query=query, selected_category=category, categories=categories)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    comments = conn.execute(
        'SELECT * FROM comments WHERE post_id = ? ORDER BY created_at DESC',
        (post_id,)
    ).fetchall()
    conn.close()
    if not post:
        flash('Post not found.', 'error')
        return redirect(url_for('index'))
    return render_template('post_detail.html', post=post, comments=comments)


@app.route('/post/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    author = request.form.get('author', '').strip() or 'Anonymous'
    content = request.form.get('content', '').strip()

    if not content:
        flash('Comment content is required.', 'error')
        return redirect(url_for('post_detail', post_id=post_id))

    conn = get_db()
    post = conn.execute('SELECT id FROM posts WHERE id = ?', (post_id,)).fetchone()
    if not post:
        conn.close()
        flash('Post not found.', 'error')
        return redirect(url_for('index'))

    conn.execute(
        'INSERT INTO comments (post_id, author, content) VALUES (?, ?, ?)',
        (post_id, author, content)
    )
    conn.commit()
    conn.close()

    flash('Comment added.', 'success')
    return redirect(url_for('post_detail', post_id=post_id))


@app.route('/comment/<int:comment_id>/edit', methods=['POST'])
def edit_comment(comment_id):
    author = request.form.get('author', '').strip() or 'Anonymous'
    content = request.form.get('content', '').strip()

    conn = get_db()
    comment = conn.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()
    if not comment:
        conn.close()
        flash('Comment not found.', 'error')
        return redirect(url_for('index'))

    if not content:
        conn.close()
        flash('Comment content is required.', 'error')
        return redirect(url_for('post_detail', post_id=comment['post_id']))

    conn.execute(
        'UPDATE comments SET author = ?, content = ?, updated_at = ? WHERE id = ?',
        (author, content, datetime.utcnow(), comment_id)
    )
    conn.commit()
    conn.close()

    flash('Comment updated.', 'success')
    return redirect(url_for('post_detail', post_id=comment['post_id']))


@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    conn = get_db()
    comment = conn.execute('SELECT post_id FROM comments WHERE id = ?', (comment_id,)).fetchone()
    if not comment:
        conn.close()
        flash('Comment not found.', 'error')
        return redirect(url_for('index'))

    conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()

    flash('Comment deleted.', 'success')
    return redirect(url_for('post_detail', post_id=comment['post_id']))

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'General').strip()
        image_url = request.form.get('image_url', '').strip()
        
        if not title or not content:
            flash('Title and content are required.', 'error')
            return render_template('post_form.html', post=None, action='Create')
        
        conn = get_db()
        conn.execute('INSERT INTO posts (title, content, category, image_url) VALUES (?, ?, ?, ?)', (title, content, category, image_url))
        conn.commit()
        conn.close()
        flash('Post published successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('post_form.html', post=None, action='Create')

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if not post:
        conn.close()
        flash('Post not found.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'General').strip()
        image_url = request.form.get('image_url', '').strip()
        
        if not title or not content:
            flash('Title and content are required.', 'error')
            return render_template('post_form.html', post=post, action='Edit')
        
        conn.execute(
            'UPDATE posts SET title=?, content=?, category=?, image_url=?, updated_at=? WHERE id=?',
            (title, content, category, image_url, datetime.utcnow(), post_id)
        )
        conn.commit()
        conn.close()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('post_detail', post_id=post_id))
    
    conn.close()
    return render_template('post_form.html', post=post, action='Edit')

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = get_db()
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    flash('Post deleted.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

#!/usr/bin/env python
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db
from app.models import ArticleType, article_types, Source, \
    Comment, Article, Role, User, Menu, ArticleTypeSetting, BlogInfo, \
    Plugin, BlogView
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


# Global variables to jiajia2 environment:
app.jinja_env.globals['ArticleType'] = ArticleType
app.jinja_env.globals['article_types'] = article_types
app.jinja_env.globals['Menu'] = Menu
app.jinja_env.globals['BlogInfo'] = BlogInfo
app.jinja_env.globals['Plugin'] = Plugin
app.jinja_env.globals['Source'] = Source
app.jinja_env.globals['Article'] = Article
app.jinja_env.globals['Comment'] = Comment
app.jinja_env.globals['BlogView'] = BlogView


def make_shell_context():
    return dict(db=db, ArticleType=ArticleType,Source=Source,
                Comment=Comment, Article=Article, User=User, Menu=Menu,
                ArticleTypeSetting=ArticleTypeSetting, BlogInfo=BlogInfo,
                Plugin=Plugin, BlogView=BlogView)

manager.add_command("shell", Shell(make_context=make_shell_context))

@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()

@manager.command
def deploy(deploy_type):
    from flask_migrate import upgrade
    from app.models import BlogInfo, User, ArticleTypeSetting, Source, \
        ArticleType, Plugin, BlogView, Comment

    # upgrade database to the latest version
    upgrade()

    if deploy_type == 'product':
        # step_1:insert basic blog info
        BlogInfo.insert_blog_info()
        # create user roles
        Role.insert_roles()
        # step_2:insert admin account
        User.insert_admin(email='blog_mini@163.com', username='blog_mini', password='blog_mini')
        # step_3:insert system default setting
        ArticleTypeSetting.insert_system_setting()
        # step_4:insert default article sources
        Source.insert_sources()
        # step_5:insert default articleType
        ArticleType.insert_system_articleType()
        # step_6:insert system plugin
        Plugin.insert_system_plugin()
        # step_7:insert blog view
        BlogView.insert_view()

    # You must run `python manage.py deploy(product)` before run `python manage.py deploy(test_data)`
    if deploy_type == 'test_data':
        # step_1:insert navs
        Menu.insert_menus()
        # step_2:insert articleTypes
        ArticleType.insert_articleTypes()
        # generate random Users
        User.generate_fake(50)
        # step_3:generate random articles
        Article.generate_fake(100)
        # step_4:generate random comments
        Comment.generate_fake(300)
        # step_5:generate random replies
        Comment.generate_fake_replies(100)
        # step_4:generate random comments
        Comment.generate_fake(300)


if __name__ == '__main__':
    manager.run()

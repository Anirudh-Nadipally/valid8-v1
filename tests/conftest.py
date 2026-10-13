import os, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("GOOGLE_API_KEY", "test-key-not-used")
os.environ.setdefault("SQLALCHEMY_DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")

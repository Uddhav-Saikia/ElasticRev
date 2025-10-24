import sys
from pathlib import Path

# Ensure project root is on sys.path so `backend` package imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from backend.database import init_database
    from backend.elasticity import ElasticityCalculator
except Exception as imp_err:
    import traceback
    traceback.print_exc()
    print('IMPORT ERROR:', imp_err)
    raise


if __name__ == '__main__':
    try:
        app = init_database()
        with app.app_context():
            try:
                res = ElasticityCalculator().calculate_elasticity(1)
                print('RESULT:', res)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print('ERROR:', e)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('ERROR DURING INIT:', e)

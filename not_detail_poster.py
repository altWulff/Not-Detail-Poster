from app import app, db, models, cli


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        models=models
    )

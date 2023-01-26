from fastapi import FastAPI


app = FastAPI(title='Checkers')

@app.get('/')
def root():
    return {'Status': 'Ok'}
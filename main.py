from app import create_app

xarya = create_app()

if __name__ == '__main__':
    xarya.run(debug=True, host="0.0.0.0", port=5000) 
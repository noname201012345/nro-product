# Hướng dẫn chạy code web nro

Yêu cầu: Cần có python (3.8) và git.
Sử dụng powershell (với Windows) hoặc terminal (Linux) để chạy.

## Tải những thứ cần thiết:

```
git clone https://github.com/kidclone3/nro-product.git
```
```
cd nro-product
```
Khởi tạo môi trường để cài các thư viện cần thiết
```
python -m venv venv
```

Với Windows, chạy:

```
venv\Scripts\activate.bat
```
Trên Unix hoặc MacOS:

```
source venv/bin/activate
```

Sau đó chạy lệnh sau để tải các thư viện cần thiết:
```
pip install -r requirements.txt
```

## Khởi tạo database
```
python init_db.py
```

## Chạy web
Lưu ý: đây chỉ là cách chạy thử, chưa phải là deploy chạy thực tế
```
python -m flask run
```

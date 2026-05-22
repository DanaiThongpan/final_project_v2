# ใช้ภาพ Python อย่างเป็นทางการจาก Docker Hub
FROM python:3.12.3

# ตั้งค่า Directory ทำงานใน Container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt เพื่อใช้ติดตั้ง dependencies
COPY requirements.txt /app/

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกไฟล์โปรเจกต์ทั้งหมดเข้าไปใน Container
COPY . /app/

# เปิดพอร์ตที่ Django ใช้โดยปกติ
EXPOSE 8000

# รันคำสั่งสำหรับจัดการฐานข้อมูลและเริ่มต้นเซิร์ฟเวอร์ Django
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

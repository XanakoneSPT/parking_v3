from rest_framework import viewsets, status
from .models import SinhVien, LichSuRaVao, LichSuNapTien, LichSuThanhToan
from .serializers import (SinhVienSerializer, LichSuRaVaoSerializer, 
                         LichSuNapTienSerializer, LichSuThanhToanSerializer)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from quan_tri_vien.models import QuanTriVien


class SinhVienViewSet(viewsets.ModelViewSet):
    queryset = SinhVien.objects.all()
    serializer_class = SinhVienSerializer

class LichSuRaVaoViewSet(viewsets.ModelViewSet):
    queryset = LichSuRaVao.objects.all()
    serializer_class = LichSuRaVaoSerializer
    
    @action(detail=False, methods=['get'], url_path='by-ma-sv/(?P<ma_sv>[^/.]+)')
    def get_by_ma_sv(self, request, ma_sv=None):
        lich_su = LichSuRaVao.objects.filter(sinh_vien__ma_sv=ma_sv)
        if not lich_su.exists():
            return Response({"message": "Không có lịch sử ra vào."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(lich_su, many=True)
        return Response(serializer.data)

class LichSuNapTienViewSet(viewsets.ModelViewSet):
    queryset = LichSuNapTien.objects.all()
    serializer_class = LichSuNapTienSerializer

class LichSuThanhToanViewSet(viewsets.ModelViewSet):
    queryset = LichSuThanhToan.objects.all()
    serializer_class = LichSuThanhToanSerializer
class NapTienAPIView(APIView):
    def post(self, request):
        serializer = LichSuNapTienSerializer(data=request.data)
        if serializer.is_valid():
            sinh_vien = serializer.validated_data['sinh_vien']
            so_tien = serializer.validated_data['so_tien']
            
            # Cập nhật số dư
            sinh_vien.so_tien_hien_co += so_tien
            sinh_vien.save()

            # Lưu lịch sử nạp tiền
            serializer.save()

            return Response({
                "message": "Nạp tiền thành công.",
                "so_du_moi": sinh_vien.so_tien_hien_co
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def login(request):
    user_id = request.data.get('ma_sv')
    password = request.data.get('password')
    
    # Kiểm tra xem có phải đang đăng nhập với tư cách quản trị viên không
    if type(user_id) == str and user_id.lower().startswith('qtv'):
    # if user_id and user_id.lower().startswith('qtv'):
        try:
            quan_tri_vien = QuanTriVien.objects.get(ma_qtv=user_id)
            if quan_tri_vien.mat_khau == password:
                return Response({
                    "message": "Đăng nhập thành công.",
                    "user_type": "admin",
                    "user_info": {
                        "ma_qtv": quan_tri_vien.ma_qtv,
                        "ho_ten": quan_tri_vien.ho_ten,
                        "vai_tro": quan_tri_vien.vai_tro
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Mật khẩu không đúng."}, status=status.HTTP_400_BAD_REQUEST)
        except QuanTriVien.DoesNotExist:
            return Response({"error": "Mã quản trị viên không tồn tại."}, status=status.HTTP_404_NOT_FOUND)

    # Xử lý đăng nhập cho sinh viên
    if not user_id or not password:
        return Response({"error": "Vui lòng cung cấp mã người dùng và mật khẩu."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        sinh_vien = SinhVien.objects.get(ma_sv=user_id)
        if sinh_vien.mat_khau != password:
            return Response({"error": "Mật khẩu không đúng."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "message": "Đăng nhập thành công.",
            "user_type": "student",
            "user_info": {
                "ma_sv": sinh_vien.ma_sv,
                "ho_ten": sinh_vien.ho_ten,
                "so_du": sinh_vien.so_tien_hien_co
            }
        }, status=status.HTTP_200_OK)
    except SinhVien.DoesNotExist:
        return Response({"error": "Mã sinh viên không tồn tại."}, status=status.HTTP_404_NOT_FOUND)
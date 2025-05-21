from rest_framework import viewsets, status
from .models import SinhVien, LichSuRaVao, LichSuNapTien, LichSuThanhToan
from .serializers import (SinhVienSerializer, LichSuRaVaoSerializer, 
                         LichSuNapTienSerializer, LichSuThanhToanSerializer)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.decorators import api_view


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
    username = request.data.get('ma_sv')
    password = request.data.get('password')
    
    if username == 'admin' and password == 'admin':
        return Response({"Message": "Đăng nhập thành công."}, status=status.HTTP_200_OK)

    if not username or not password:
        return Response({"error": "Vui lòng cung cấp tên đăng nhập và mật khẩu."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        sinhVien = SinhVien.objects.get(ma_sv=username)
    except sinhVien.DoesNotExist:
        return Response({"error": "Mã sinh viên không tồn tại."}, status=status.HTTP_404_NOT_FOUND)

    if sinhVien.mat_khau != password:
        return Response({"error": "Mật khẩu không đúng."}, status=status.HTTP_400_BAD_REQUEST)


    return Response({"Message": "Đăng nhập thành công."}, status=status.HTTP_200_OK)
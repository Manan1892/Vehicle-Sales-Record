# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from myapp.models import Make, Model, VehicleInfo, SaleInfo
from django.contrib.auth.models import User
from django.http import QueryDict
from datetime import datetime
import json
from django.db.models import Q

from myapp.serializers import RegistrationSerializer, UserLoginSerializer, TokenSerializer,\
    MakeSerializer, ModelSerializer,ModelPostSerializer, VehicleSerializer, VehicleInfoSerializer,\
    SaleSerializer, SaleInfoSerializer

class UserRegistrationAPIView(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user = serializer.instance
        user.set_password(request.data['password'])
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        data = serializer.data
        data["token"] = token.key

        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class UserLoginAPIView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                data=TokenSerializer(token).data,
                status=status.HTTP_200_OK,
            )
        else:

            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

class UserLogoutAPIView(APIView):

    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)

class MakeView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get_object(self, pk):
        try:
            return Make.objects.get(pk=pk)
        except Make.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        if pk:
            make = self.get_object(pk)
            make = MakeSerializer(make)
            return Response(make.data)
        else:
            makes = Make.objects.all()
            makes = MakeSerializer(makes, many=True)
            return Response(makes.data)

    def post(self, request):
        serializer = MakeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        make = self.get_object(pk)
        serializer = MakeSerializer(make, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        make = self.get_object(pk)
        make.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ModelView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get_object(self, pk):
        try:
            return Model.objects.get(pk=pk)
        except Model.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        if pk:
            model = self.get_object(pk)
            model = ModelSerializer(model)
            return Response(model.data)
        else:
            model = Model.objects.all()
            model = ModelSerializer(model, many=True)
            return Response(model.data)

    def post(self, request):
        serializer = ModelPostSerializer(data=request.data)
        if serializer.is_valid():
            make = None
            try:
                make = Make.objects.get(name=request.data['make'])

            except Make.DoesNotExist:
                return Response({'msg':'Invalid Make Name'}, status=status.HTTP_200_OK)

            inst = Model(**dict(name=request.data['name'],make=make))
            inst.save()
            serializer = ModelSerializer(inst)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        Model = self.get_object(pk)
        serializer = ModelSerializer(Model, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        Model = self.get_object(pk)
        Model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VehicleInfoView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def validate_vin(self, field):
        """
        Validate a VIN against the 9th position checksum
        See: http://en.wikipedia.org/wiki/Vehicle_Identification_Number#Check_digit_calculation
        """
        POSITIONAL_WEIGHTS = [8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2]
        ILLEGAL_ALL = ['I', 'O', 'Q']
        ILLEGAL_TENTH = ['U','Z','0']
        LETTER_KEY = dict(
            A=1,B=2,C=3,D=4,E=5,F=6,G=7,H=8,
            J=1,K=2,L=3,M=4,N=5,    P=7,    R=9,
                S=2,T=3,U=4,V=5,W=6,X=7,Y=8,Z=9,
        )
        if len(field) == 17:
            vin = field.upper()

            for char in ILLEGAL_ALL:
                if char in vin:
                    return {'msg':'Field cannot contain "I", "O", or "Q".'}

            if vin[10] in ILLEGAL_TENTH:
                return {'msg':'Field cannot contain "U", "Z", or "0" in position 10.'}

            check_digit = vin[8]

            pos = sum =0
            for char in vin:
                value = int(LETTER_KEY[char]) if char in LETTER_KEY else int(char)
                weight = POSITIONAL_WEIGHTS[pos]
                sum += (value * weight)
                pos += 1
            calc_check_digit = int(sum) % 11

            if calc_check_digit == 10:
                calc_check_digit = 'X'

            if str(check_digit) != str(calc_check_digit):
                return {'msg':'Invalid VIN.'}
            else:
                return True
        else:
            return {'msg':'Vin Field must be 17 characters.'}

    def get_object(self, pk):
        try:
            return VehicleInfo.objects.get(pk=pk)
        except VehicleInfo.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        if pk:
            vehicleInfo = self.get_object(pk)
            vehicleInfo = VehicleInfoSerializer(vehicleInfo)
            return Response(vehicleInfo.data)
        else:
            vehicleInfo = VehicleInfo.objects.all()
            vehicleInfo = VehicleInfoSerializer(vehicleInfo, many=True)
            return Response(vehicleInfo.data)

    def post(self, request):
        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            make = None
            model = None
            try:
                make = Make.objects.get(name=request.data['make'])

            except Make.DoesNotExist:
                return Response({'msg':"Make doesn't exist"}, status=status.HTTP_200_OK)

            try:
                model = Model.objects.get(name=request.data['model'])

            except Model.DoesNotExist:
                return Response({'msg':'Invalid Model Id'}, status=status.HTTP_200_OK)

            resp = self.validate_vin(field=request.data['vin'])
            if resp == True:
                inst = VehicleInfo(**dict(vin=request.data['vin'],make=make,model=model,year=request.data['year']))
                inst.save()
                serializer = VehicleInfoSerializer(inst)
            else:
                return Response(resp,status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        vehicleInfo = self.get_object(pk)
        serializer = VehicleInfoSerializer(vehicleInfo, data=request.data)
        if serializer.is_valid():
            resp = self.validate_vin(field=request.data['vin'])
            if resp == True:
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(resp,status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        vehicleInfo = self.get_object(pk)
        vehicleInfo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FilterView(APIView):

    def get(self,request):
        inst = SaleInfo.objects.filter(Q(seller=request.user) | Q(buyer=request.user))
        serializer = SaleInfoSerializer(inst, many=True)
        return Response(serializer.data)

    def post(self,request):
        data = request.data
        kwargs = {}
        for key,val in data.items():
            if val != '':
                if key == 'seller':
                    kwargs['seller__first_name__icontains'] = val
                elif key == 'buyer':
                    kwargs['buyer__first_name__icontains'] = val
                elif key == 'price':
                    kwargs['price__lte'] = val
                elif key == 'sale_date':
                    dt = datetime.strptime(val, "%Y-%m-%d").date()
                    kwargs['sale_date__date__lte'] = dt
                elif key == 'dealership':
                    kwargs['seller__UserInfo__dealership'] = val
                    kwargs['buyer__UserInfo__dealership'] = val
                elif key == 'make':
                    kwargs['vehicle__make__name'] = val
                elif key == 'model':
                    kwargs['vehicle__model__name'] = val
                elif key == 'vin':
                    resp = self.validate_vin(field=request.data['vin'])
                    if resp == True:
                        kwargs['vehicle__vin'] = val
                    else:
                        return Response(resp,status=status.HTTP_400_BAD_REQUEST)
                elif key == 'year':
                    kwargs['vehicle__year'] = val
                else:
                    kwargs[key] = val

        inst = SaleInfo.objects.filter(**kwargs)
        serializer = SaleInfoSerializer(inst, many=True)
        return Response(serializer.data)

class SaleInfoFileView(APIView):

    def post(self,request):
        data = request.FILES['file'].read()
        result = []

        for i in json.loads(data):
            seller = None
            buyer = None
            vehicle = None
            try:
                seller = User.objects.get(first_name=i['seller'])

            except User.DoesNotExist:
                return Response({'msg':'Invalid Seller Id'}, status=status.HTTP_200_OK)

            try:
                buyer = User.objects.get(first_name=i['buyer'])

            except User.DoesNotExist:
                return Response({'msg':'Invalid Buyer Id'}, status=status.HTTP_200_OK)

            try:
                vehicle = VehicleInfo.objects.get(vin=i['vehicle'])

            except VehicleInfo.DoesNotExist:
                return Response({'msg':'Invalid VehicleInfo Id'}, status=status.HTTP_200_OK)

            inst = SaleInfo(**dict(price=i['price'],seller=seller,buyer=buyer,vehicle=vehicle))
            inst.save()
            result.append(inst)
        saleInfo = SaleInfoSerializer(result, many=True)
        return Response(saleInfo.data)

class SaleInfoView(APIView):

    def get_object(self, pk):
        try:
            return SaleInfo.objects.get(pk=pk)
        except SaleInfo.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        if pk:
            saleInfo = self.get_object(pk)
            saleInfo = SaleInfoSerializer(saleInfo)
            return Response(saleInfo.data)

        else:
            saleInfo = SaleInfo.objects.all()
            saleInfo = SaleInfoSerializer(saleInfo, many=True)
            return Response(saleInfo.data)

    def post(self, request):
        serializer = SaleSerializer(data=request.data)
        if serializer.is_valid():
            seller = None
            buyer = None
            vehicle = None
            try:
                seller = User.objects.get(id=request.data['seller'])

            except User.DoesNotExist:
                return Response({'msg':'Invalid Seller Id'}, status=status.HTTP_200_OK)

            try:
                buyer = User.objects.get(id=request.data['buyer'])

            except User.DoesNotExist:
                return Response({'msg':'Invalid Buyer Id'}, status=status.HTTP_200_OK)

            try:
                vehicle = VehicleInfo.objects.get(id=request.data['vehicle'])

            except VehicleInfo.DoesNotExist:
                return Response({'msg':'Invalid VehicleInfo Id'}, status=status.HTTP_200_OK)

            inst = SaleInfo(**dict(price=request.data['price'],seller=seller,buyer=buyer,vehicle=vehicle))
            inst.save()

            serializer = SaleInfoSerializer(inst)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        saleInfo = self.get_object(pk)
        serializer = SaleInfoSerializer(saleInfo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        saleInfo = self.get_object(pk)
        saleInfo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

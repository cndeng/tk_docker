from django.shortcuts import render,HttpResponse
from django.http import StreamingHttpResponse
from lib import docker_main
from lib import config
from django.utils.safestring import mark_safe
import datetime,time
import os,zipfile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from collections import deque
# Create your views here.
@login_required
def LogNow(request):
    # 接收前端传递参数进行计算返回渲染后的页面
    if request.method == 'GET':
        FindTime = ''
        Hostname = request.GET.get('hostname')
        ContainerName = request.GET.get('container_name')
        log_type = request.GET.get('log_type')
        if log_type == 'log_info':
            if request.GET.get('find_time'):
                FindTime = request.GET.get('find_time')
            logs = DockerLog(Hostname, ContainerName, FindTime)
            logs_str = mark_safe(str(logs, encoding="utf-8"))
            info = {'logs': logs_str,'log_type':log_type ,'hostname': Hostname, 'container_name': ContainerName}
            return render(request, 'log/lognow.html', info)
            # 获取到了容器的name 然后去lib中搜索name的容器然后进行日志打印
        elif log_type == 'log_error':
            docker_download_log_path = DockerUpdateALog(Hostname, ContainerName, log_type)
            f = open(docker_download_log_path['return_results'])
            log_format = f.readlines()
            log_format = deque(log_format, 500)
            log_all = ''
            for i in log_format:
                log_all = log_all + i
            print(log_all)
            info = {'logs': log_all,'log_type':log_type , 'hostname': Hostname, 'container_name': ContainerName}
            return render(request, 'log/lognow.html', info)

def DockerLog(Hostname, ContainerName, FindTime):
    # 调取所有容器判断健康度，然后返回日志.
    DockerContainerAll = docker_main.DockerInitial().DockerContainerCictionary()
    ContainerAll = DockerContainerAll[Hostname]
    for i in ContainerAll:
        if i.name == ContainerName:
            if FindTime:
                FindTime = int(FindTime)
                DatetimeNow = datetime.datetime.now() + datetime.timedelta(minutes=-FindTime,hours=-8)
                b_logs = i.logs(since=DatetimeNow)
                return b_logs
            else:
                b_logs = i.logs(tail=config.log_tail_line)
                return b_logs

@login_required
def LogDump(request):
    # 当天日志的下载以及全部的日志备份
    if request.method == 'GET':
        all_log = request.GET.get('all_log')
        hostname = request.GET.get('hostname')
        container_name = request.GET.get('container_name')
        log_type = request.GET.get('log_type')
        if all_log:
            docker_log_bak = DockerUpdateAllLog()
            return render(request, 'log/downandback.html', docker_log_bak)
        elif hostname and container_name and log_type:
            print(hostname,container_name)
            docker_download_log_path = DockerUpdateALog(hostname=hostname,container_name=container_name,log_type=log_type)
            print(docker_download_log_path)
            return render(request, 'log/downandback.html', docker_download_log_path)
        else:
            errors = {'return_results': '参数传递有错误！请检查!', 'log_name': None}
            return render(request, 'log/downandback.html', errors)
    return HttpResponse('出错了~')

#docker log的备份，分两种方式，一种是所有的日志全部备份在升级前，第二种是开发人员查看当天的日志需要进行下拉下载操作临时文件都保存在了tmp目录下
def DockerUpdateAllLog():
    # 全部日志备份
    docker_container_all = docker_main.DockerInitial().DockerContainerCictionary()
    for i in docker_container_all:
        for y in docker_container_all[i]:
            service_name = y.name.split('-')[0]
            if y.status == 'running':
                if service_name in config.service_name_list:
                    service_name = service_name + '-service'
                    log_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    service_log_path = '/logs/' + service_name + '/log_info.log'
                    log_init = y.get_archive(service_log_path)
                    log_str = str(log_init[0].data, encoding="utf-8")
                    log_dir_master = config.log_dir_master
                    log_local_name = log_dir_master +'/'+ service_name + '/update/'+'update'+ i + '-' + service_name + '-' + log_date + '.log'
                    log_file = open(log_local_name, 'a+')
                    date_now = str(datetime.datetime.now())
                    log_file.write('执行时间:' + date_now)
                    log_file.write(log_str)
                    log_file.close()
    return_results = {'return_results': '!备份成功!返回主页!', 'log_name': None}
    return return_results

def DockerUpdateALog(hostname,container_name,log_type):
    # 某个容器的日志下载
    docker_container_all = docker_main.DockerInitial().DockerContainerCictionary()
    for i in docker_container_all[hostname]:
        if i.name == container_name:
            service_name = i.name.split('-')[0]
            service_name = service_name + '-service'
            if i.status == 'running':
                log_date = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
                print(log_date,service_name,log_type)
                service_log_path = '/logs/' + service_name + '/'+log_type+'.log'
                print('/logs/' + service_name + '/'+log_type+'.log')
                log_init = i.get_archive(service_log_path)
                log_str = str(log_init[0].data, encoding="utf-8")
                log_name = hostname + '-' + service_name + '-' + log_date + '-' +  log_type + '.log'
                log_dir_master = config.log_dir_master
                log_path = log_dir_master + '/'+'tmp/' + log_name
                log_file = open(log_path, 'a+')
                date_now = str(datetime.datetime.now())
                log_file.write('执行时间:' + date_now+'\n')
                log_file.write(log_str)
                log_file.close()
                return_results = {'return_results': log_path, 'log_name': log_name}
                return return_results
            else:
                return_results = {'return_results': None, 'log_name': 'docker容器状态为exit，请检查！'}
                return return_results

@login_required
def LogDownload(request):
    if request.method == 'GET':
        log_path = request.GET.get('log_path')
        log_name = request.GET.get('log_name')
        print('log_path:', log_path, 'log_name:', log_name)
        # 定义zip文件名称。
        zip_file_name = log_name + '.zip'
        # 打包文件后置放的目录地址。
        zip_dir = config.log_dir_master + '/' + 'tmp/' + zip_file_name
        archive = zipfile.ZipFile(zip_dir, 'w', zipfile.ZIP_DEFLATED)
        # 写入zip中文件的地址及名称
        archive.write(log_path)
        # 写入结束
        archive.close()
        print(zip_dir)
        if os.path.isfile(zip_dir):
            response = StreamingHttpResponse(readFile(zip_dir))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{0}"'.format(zip_file_name)
            return response
        else:
            return HttpResponse('没有这个文件')

def readFile(filename, chunk_size=512):
    with open(filename, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break

@login_required
def LogDir(request):
    if request.method == 'GET':
        log_list = config.service_name_list
        service_name_all = []
        for i in log_list:
            y = i + '-service'
            service_name_all.append(y)
        print(service_name_all)
        return render(request, 'log/logdir.html', {'service_now': service_name_all})

@login_required
def LogDirPage(request):
    service_name = request.GET.get('service_name')
    log_type = request.GET.get('log_type')
    sort = request.GET.get('sort')
    print(sort)
    # if not sort:
    #     sort = '1'

    print(service_name, log_type)
    log_path = config.log_dir_master
    service_name_path = log_path + '/' + service_name + '/' + log_type
    all_file = []
    for i in os.listdir(service_name_path):
        file_path = service_name_path + '/' + i
        if os.path.isfile(file_path):
            file_create_time = os.path.getctime(file_path)
            time_struct = time.localtime(file_create_time)
            time_24 = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
            all_file.append([i, file_path,time_24])
    print('all_file:',all_file)
    if sort:
        all_file = sorted(all_file, key=lambda file_name: file_name[2], reverse=True)
    else:
        all_file = sorted(all_file, key=lambda file_name: file_name[1], reverse=True)
    paginator = Paginator(all_file, 13)  # Show 25 contacts per page
    page = request.GET.get('page')
    information = [{'service_name': service_name, 'log_type': log_type,'sort':sort}]
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'log/catdownlog.html', {"contacts": contacts, 'information': information})
# @login_required
# def LogDirPage(request):
#     service_name = request.GET.get('service_name')
#     log_type = request.GET.get('log_type')
#     print(service_name,log_type)
#     log_path = config.log_dir_master
#     service_name_path = log_path + '/' + service_name + '/' + log_type
#     all_file = []
#     for i in os.listdir(service_name_path):
#         file_path = service_name_path + '/' + i
#         if os.path.isfile(file_path):
#             all_file.append([i, file_path])
#     print(all_file)
#     all_file = sorted(all_file, key=lambda file_name: file_name[1])
#     paginator = Paginator(all_file, 13)  # Show 25 contacts per page
#     page = request.GET.get('page')
#     information = [{'service_name':service_name,'log_type':log_type}]
#     try:
#         contacts = paginator.page(page)
#     except PageNotAnInteger:
#         contacts = paginator.page(1)
#     except EmptyPage:
#         contacts = paginator.page(paginator.num_pages)
#     return render(request, 'log/catdownlog.html', {"contacts": contacts, 'information': information})

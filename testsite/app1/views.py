from django.shortcuts import render
from django.http import HttpResponse
import ansible_runner

def index(request):
    if request.method == 'POST':
        with open("/home/localadmin/ald-servers-install/inventory/hosts", mode="w", encoding="utf-8") as out:
            out.write(render(request, 'hosts.j2', {}))
        # a = ansible_runner.run(
        #     private_data_dir="/home/localadmin/ald-servers-install", 
        #     playbook="playbook.yaml", 
        #     quiet=True,
        # )
        # return render(request, 'finish.html', { 'status': a.status, })
        return render(request, 'finish.html', { 'status': "ok!", })
    return render(request, 'index.html', {})

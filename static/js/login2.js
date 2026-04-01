function login2(){
    var username = document.getElementById("ID").value;
    var password = document.getElementById("PASSWORD").value;
    if(username==""){
        $.jGrowl("用户名不能为空！", { header: '提醒' });
    }else if(password==""){
        $.jGrowl("密码不能为空！", { header: '提醒' });
    }else{
        AjaxFunc();
    }
}
function AjaxFunc()
{
    var username = document.getElementById("ID").value;
    var password = document.getElementById("PASSWORD").value;
    $.ajax({
        type: 'POST',
        url: "/dologin2",
        data: {"username": username,"password": password},
        success: function (data) {

             if(data.statu){
                    window.location.href = '/index2';
                    alert("登录成功");
                } else {
                    alert("登录失败");
                }
        },
        error: function (xhr, type) {
            alert('登陆失败');
            window.location.reload();


        }
    });
}
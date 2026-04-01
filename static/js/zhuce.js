function zhuce() {
    var username = document.getElementById("ID").value;
    var password = document.getElementById("PASSWORD").value;
    if (username == "") {
        $.jGrowl("用户名不能为空！", {header: '提醒'});
    } else if (password == "") {
        $.jGrowl("密码不能为空！", {header: '提醒'});
    } else {
        $.ajax({
            type: 'POST',
            url: "/dozhuce",
            dataType: 'json',
            data: {"username": username, "password": password},
            success: function (data) {
                if (data.statu) {
                    window.location.href = '/';
                    alert("注册成功");
                } else {
                    alert("用户已存在");
                }
                // if data。statu']
                //
                // else：

            },
            error: function (xhr, type) {
                alert('注册失败');
                window.location.reload();
            }
        });
    }
}
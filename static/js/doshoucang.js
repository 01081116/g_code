function collectSong(singerid) {
    $.ajax({
        type: 'POST',
        url: '/songer_list',
        data: {'singer_id': singerid},
        success: function(data) {
            if (data.status) {
                alert('收藏成功');

            } else {
                alert('收藏失败');
            }
        },
        error: function(xhr, status, error) {
            alert('发生错误： ' + error);
        }
    });
}
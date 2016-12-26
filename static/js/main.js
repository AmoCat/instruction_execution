var context = {};
var callback = "";

var get_reply = function() {
    $('#send').addClass('disabled');
    var sent = $('#input-box').val();
    $('#input-box').val("");
    $.ajax({
      type: 'POST',
      contentType: 'application/json',
      url: 'module/instruction_execution/bus',
      data: JSON.stringify({
        content: sent,
        context: context,
      }),
      success: function(data) {
        var reply = "";
        if (data['status'] == 0) {
          reply = data['reply'].replace(/\n/g, "<br>");
          context = {};
        }
        else if (data['status'] == 1) {
          reply = data['reply'];
          callback = data['callback'];
          context = data['context'];
        } else {
          reply = "[多轮会话中断，使用其它模块回复]";
          context = {};
        }
        $('#reply-box').prepend("<tr><td>" + sent + "</td><td>" + reply + "</td><td>"+ JSON.stringify(data['context']) +"</td></tr>");
        $('#send').removeClass('disabled');
      },
      error: function(xhr, textStatus, error) {
        $('#reply-box').prepend("<tr><td>" + sent + "</td><td>" + error + "</td><td>"+ context['error_msg'] +"</td></tr>");
        console.log(xhr.statusText);
        console.log(textStatus);
        console.log(error);
        context = {};
        $('#send').removeClass('disabled');
      }
    });
};

$(document).ready(function() {
  $('#send').click(get_reply);
  $('#input-box').bind('keypress', function(event){
    if (event.keyCode == "13"){
      get_reply();
    }
  });
});

let i=0

$("button").prop("disabled", false).click(function() {
    i++
    if (i%5 == 0) {
        $(".slides").html($(".slides").html()+"<div style=\"background-color:green;\" id=\"slide-"+i+"\">lol</div>")
    }
    else
        $(".slides").html($(".slides").html()+"<div id=\"slide-"+i+"\">"+i+"</div>")
})
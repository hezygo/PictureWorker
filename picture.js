var speed = 600;

var getImgArr = function() {
    return document.querySelectorAll('img.rich_pages');
}
var flush = function() {
    var imgArr = getImgArr();
    imgArr.forEach(function(img, index) {
        setTimeout(function() {
            img.scrollIntoView();
        }, speed * index) 
    })
}
var checkRealSrc = function() {
    var imgArr = getImgArr();
    var bool = true;
    imgArr.forEach(function(x) {
        if(x.getAttribute('src').slice(0,4) != 'http') {
            bool = false;
        }
    });
    return bool;
}
var waitAllLoading = function() {
    var imgArr = getImgArr();
    flush();
    setTimeout(function() {
        if(!checkRealSrc()) {
            waitAllLoading();
        }else  {
            window.jojoImgAllLoading = 'Done';
        }
    }, speed * imgArr.length)
}

waitAllLoading();

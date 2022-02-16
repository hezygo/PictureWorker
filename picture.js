(async function() {
    var sleep = function(time) {
        return new Promise(function(resolve) {
            setTimeout(function() {
                resolve()
            }, time)
        })
    }

    var checkRealSrc = async function(src) {
        if(src.slice(0, 9) == 'data:image') {
            return false
        }
        if(src.slice(0, 4) == 'http') {
            return true
        }
        return false
    }



    var imgArr = document.querySelectorAll('img.rich_pages')

    imgArr.forEach(img => {
        (async function(){
            img.scrollIntoView()


            
            await sleep(200)
            var bool = checkRealSrc(img.getAttribute('src'))




            var realSrc = img.getAttribute('src')
            console.log(realSrc)
        })()
    })

})()





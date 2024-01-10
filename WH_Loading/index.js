function domReady(fn) {
    if (document.readyState==="complete"|| document.readyState==="interactive") {
        setTimeout(fn,1)
    } else {
        document.addEventListener("DOMContentLoaded",fn)
    }
}

domReady(function(){
    var myqr = document.getElementById('result')
    var lastResult, countResult = 0;

    function onScanSuccess(decodeText, decodeResult){
        if (decodeText !== lastResult) {
            ++countResult;
            lastResult = decodeResult;
            alert("your QR is:" + decodeText, decodeResult)
            myqr.innerHTML='you scan ${countResult} : ${decodeText}'
        }
    }

    var htmlscanner = new Html5QrcodeScanner('reader', {fps:20, qrbox:250})
    htmlscanner.render(onScanSuccess)
}) 
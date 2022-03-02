var calculator = Desmos.GraphingCalculator(document.getElementById('calculator'));
var frames = {}; getFrames()
var settings = {}; getSettings()
var size = 0; getSize()
var defaultState; getDefaultState()

//Load all the bezier curve data
async function getFrames() {
    await $.ajax({
        url: 'static/frames.json',
        type:'GET',
        dataType: 'json',
        success: (data) => {
            frames = data
        }
    })
}

//Load the graph settings
async function getSettings() {
    await $.ajax({
        url: 'static/settings.json',
        type:'GET',
        dataType: 'json',
        success: (data) => {
            settings = data['frontend']
        }
    })
}

//Get the total number of equations to render
async function getSize() {
    let timer = ms => new Promise(res => setTimeout(res, ms))
    while(jQuery.isEmptyObject(frames)) await timer(500)

    for(frame in frames) {
        for(eq in frames[frame]) size++
    }
}

//Set the calculator's viewport settings
async function getDefaultState() {
    let timer = ms => new Promise(res => setTimeout(res, ms))
    while(jQuery.isEmptyObject(settings)) await timer(500)
    
    calculator.setMathBounds({
        top: Number(settings.top),
        bottom: Number(settings.bottom),
        left: Number(settings.left),
        right: Number(settings.right)
    })
    calculator.showGrid = Boolean(settings.grid)//TODO doesn't work
    defaultState = calculator.getState()
    draw(frames['1'], 1, save=false)
}

calculator.observe('graphpaperBounds', () => {
    let bounds = calculator.graphpaperBounds.mathCoordinates
    document.getElementById('top-input').value = Math.floor(bounds.top)
    document.getElementById('bottom-input').value = Math.floor(bounds.bottom)
    document.getElementById('left-input').value = Math.floor(bounds.left)
    document.getElementById('right-input').value = Math.floor(bounds.right)
})



//Start rendering the frames in desmos
async function start() {
    let start = new Date()
    let showTime = setInterval(() => {
        let time = new Date() - start

        let hours = Math.floor(time / 3600000)
        time = time % 3600000
        let minutes = Math.floor(time / 60000)
        time = time % 60000
        let seconds = Math.floor(time / 1000)
        time = time % 1000
        
        let showTime = document.getElementById('time')
        showTime.innerText = `${String(hours).padStart(2, '0')} : ${String(minutes).padStart(2, '0')} : ${String(seconds).padStart(2, '0')}`
    }, 1000)

    let timer = ms => new Promise(res => setTimeout(res, ms))
    for(frame in frames) {
        draw(frames[frame], frame)
        await timer(Object.keys(frames[frame]).length * 5)
    }
    clearInterval(showTime)

    alert('Done')
    await $.ajax({
        url: '/finish',
        type: 'GET',
    })
    document.getElementById('video').click()
}

let n = 0
function draw(frame, m, save=true) {
    calculator.setBlank()
    calculator.setState(defaultState)
    for(eq in frame) {
        calculator.setExpression({latex: frame[eq], color: settings.color})
        if(save) n++
    }
    progress(n, m)
    if(save) {
        calculator.asyncScreenshot({
            width: 1920,
            height: 1080,
            mode: 'stretch'
        }, saveIMG)
    }
}

function progress(eqs, m) {
    let frame = document.getElementById('fraction')
    let fill = document.getElementById('fill')
    
    frame.innerText = `${Number(m)}/${Object.keys(frames).length}`
    fill.style.width = `${(eqs / size) * 100}%`
}

//Save the frame
var frame = 1
function saveIMG(dataURI) {
    $.ajax({
        url: '/download',
        type: 'POST',
        data: JSON.stringify({
            data: dataURI,
            frame: frame
        }),
        processData: false,
        contentType: "application/json",
    })
    frame++
}
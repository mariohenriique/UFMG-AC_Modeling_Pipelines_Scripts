// Adicionar novo campo para inserção de imagens
var imageIndex = 0
function addImageField() {
    let imageFields = document.getElementById("image-fields")
    let imageField = document.createElement("div")

    imageField.className = "image-field"
    imageField.innerHTML = '<label for="id_imagens-' + imageIndex + '-image">Imagem:</label>' +
    '<input type="file" name="imagens-' + imageIndex + '-image" id="id_imagens-' + imageIndex + '-image">' +
    '<br>' +
    '<label for="id_imagens-' + imageIndex + '-legenda">Legenda:</label>' +
    '<textarea name="imagens-' + imageIndex + '-legenda" id="id_imagens-' + imageIndex + '-legenda"></textarea>'
    imageFields.appendChild(imageField)
    imageIndex++
    document.getElementById("image-count-field").innerHTML = imageIndex
    document.getElementById("image-count-field").value = imageIndex
}

// Mudar a cor do fundo quando selecionar qual imagem deletar
function marcada(id_image) {
    var imageClickada = document.getElementById('delete-image-'+id_image)
    var paragrafoClickada = imageClickada.parentNode
    console.log(paragrafoClickada)
    if (imageClickada.checked){
        paragrafoClickada.style.backgroundColor = 'blue'
    } else{
        paragrafoClickada.style.backgroundColor = ''
    }
}

document.getElementById('dateIdentified').addEventListener('change', function() {
var dateIdentified = new Date(document.getElementById('dateIdentified').value)
var dateIdentifiedEnd = document.getElementById('id_dateIdentifiedEnd')
dateIdentifiedEnd.min = formatDate(dateIdentified)
})
function formatDate(date) {
    var month = '' + (date.getMonth() + 1)
    var day = '' + (date.getDate() + 1)
    var year = date.getFullYear()
    if (month.length < 2) month = '0' + month
    if (day.length < 2) day = '0' + day
    return [year, month, day].join('-')
}

// Counter to keep track of the number of URL input fields
let urlCount = 0

function addUrlField() {
    urlCount++
    const urlContainer = document.getElementById("url-container")
    const newUrlInput = document.createElement("input")
    newUrlInput.type = "text"
    newUrlInput.name = "dados_geneticos[]"
    newUrlInput.id = `dados_geneticos-${urlCount}`
    urlContainer.appendChild(newUrlInput)
}
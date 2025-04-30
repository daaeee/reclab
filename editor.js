let buttonElementAdd = document.querySelector('[data-js-main-container-add]')
let sectionElement = document.querySelector('[data-js-main-container-section]:last-of-type')
let formElement = document.querySelector('[data-js-main-container]')
let mainElement = document.querySelector('[data-js-main]')

const addEl = () => {
    mainElement.insertAdjacentHTML('aftereend', formElement.outerHTML)
}

// console.log(mainElement)
// console.log(formElement)

let containerCnt = 1
let boxOld = ''
let boxNew = ''
let objname, comname, comment, deleteBtn = ''
let del = /box-delete/
let flag = 0

document.addEventListener('click', (event) => {
    if (event.target.classList.contains("box-add")) {
        sectionElement = document.querySelector('[data-js-main-container-section]:last-of-type')
        sectionElement.insertAdjacentHTML('afterend', sectionElement.outerHTML)
        sectionElement = document.querySelector('[data-js-main-container-section]:last-of-type')
        boxOld = `box-form-container-${containerCnt}`

        containerCnt += 1

        boxNew = `box-form-container-${containerCnt}`
        objname = `objname-${containerCnt}`
        comname = `comname-${containerCnt}`
        comment = `comment-${containerCnt}`
        deleteBtn = `box-delete-${containerCnt}`

        sectionElement.classList.replace(boxOld, boxNew)
        sectionElement.querySelector("[section-objnameinput]").id = objname
        sectionElement.querySelector("[section-objnameinput]").setAttribute('name', objname)
        sectionElement.querySelector("[section-objnamelabel]").setAttribute('for', objname)

        sectionElement.querySelector("[section-comnameinput]").id = comname
        sectionElement.querySelector("[section-comnameinput]").setAttribute('name', comname) 
        sectionElement.querySelector("[section-comnamelabel]").setAttribute('for', comname)

        sectionElement.querySelector("[section-commentinput]").id = comment
        sectionElement.querySelector("[section-commentinput]").setAttribute('name', comment)
        sectionElement.querySelector("[section-commentlabel]").setAttribute('for', comment)

        // sectionElement.querySelector("[section-deleteBtn]").setAttribute('class', deleteBtn)
        flag += 1
    }
})

document.addEventListener('click', (event) => {
    if (!flag) {
        console.log("Nononono")
        return
    }

    if (event.target.classList.contains("box-delete") && flag>0) {
        event.target.parentNode.remove()
        flag -= 1
        return
    }
})
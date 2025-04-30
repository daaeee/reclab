const openBtn = document.querySelector('[data-js-header-open]')
const closeBtn = document.querySelector('[data-js-header-dialog-close]')

// console.log(openBtn)
// console.log(closeBtn)

// openBtn.addEventListener('click', () => {
//     modal.showModal()
// })

// closeBtn.addEventListener('click', () => {
//     modal.close()
// })

document.querySelectorAll('[data-modal-open]').forEach(button => {
    const id = button.dataset.modalOpen;
    const modal = document.querySelector(`[data-modal="${id}"]`);
    if(modal){
      button.addEventListener('click', () => {
        modal.showModal();
        document.body.classList.add('lock')
      });
      const closeButton = modal.querySelector('.close');
      if(closeButton){
        closeButton.addEventListener('click', () => {
          modal.close();
          document.body.classList.remove('lock')
        });
      }
      modal.addEventListener('click', (e) => {
        const modal = e.currentTarget
        const isClickOnBackDrop = e.target === modal

        if(isClickOnBackDrop) {
          modal.close()
          document.body.classList.remove('lock')
        }
      })
    }
  });


let accountBtn = document.querySelector("[data-js-accountBtn]")
let menu = document.querySelector("[data-js-accountMenu]")

console.log(accountBtn)

let flag2 = false

accountBtn.addEventListener('click', () => {
    if (flag2) {
        menu.style.cssText += `
            display: none;
        `
        flag2 = false
    }
    else {
        menu.style.cssText += `
            display: grid;
        `
        flag2 = true
    }
})

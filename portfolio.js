
document.addEventListener('DOMContentLoaded', function(){
    // Automatically show homepage and hide all other divs
        showsection("home");
    
    // Select all links
    document.querySelectorAll('.nav-link').forEach(navlink =>{

        // When link is clicked, update active tab and show this section

        navlink.onclick = function(){
            document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
            this.classList.add('active');
            showsection(this.dataset.section);
        }
    })
})

function showsection(section){
    // Hide all other sections
    document.querySelectorAll('.section').forEach(div => {
        div.style.display ='none';
    });
    // Show relevant section
    section = document.getElementById(section);
    section.style.display='flex';
    spec = section.querySelector('.spec');
    
    if (spec) {
    spec.style.display='flex';
    }
    
   
}

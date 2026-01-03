// To help with debugging errors, I used CS50 Duck Debugger
document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

   //By default, load the inbox
  load_mailbox('inbox');

 // Send emails
  document.querySelector('#send-email').addEventListener('click',send_email);

});

function send_email(event){
     event.preventDefault();
     console.log('Prevent reload');
  // Send emails
     fetch('/emails', {
        method: 'POST',
        redirect: 'manual',
        body: JSON.stringify({
          recipients: document.querySelector('#compose-recipients').value,
          subject : document.querySelector('#compose-subject').value,
          body: document.querySelector('#compose-body').value,
           })
          })
      .then(response => response.json())
      .then(result =>{
        console.log(result);
         // Redirect to sent mailbox
        return load_mailbox('sent');
      });

    }

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

    }


function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    console.log(emails);
    emails.forEach(email => add_email(email, mailbox));
  });

}

function add_email(contents, mailbox){
  // Create new div for email and add appopriate styling
  const email = document.createElement('div');

  email.className = 'email';
  email.innerHTML = `<div style="font-weight: bold; margin-right:15px;"> ${contents["sender"]} </div>`;
  email.innerHTML += `<div style="margin-left: 15px;">${contents["subject"]}</div>`;
  email.innerHTML += `<div style="margin-left: auto;">${contents["timestamp"]}</div>`;
  email.style.border = "solid grey";
  email.style.borderWidth= "thin";
  email.style.margin = "15px 0;"
  email.style.display = "flex";
  email.style.flexDirection = "row";
  email.style.justifyContent = "flex-start";

  // Update color of background if it is read or not

  if (contents["read"] == true){
    email.style.backgroundColor = "grey";
    email.style.border = "white";

  }
  else {
    email.style.backgroundColor = "white";
    email.style.border = "solid grey";
  }

  // Add event listener to each email
  email.addEventListener('click', () => view_email_contents(contents, mailbox));

    // Add email to section
  document.querySelector('#emails-view').append(email);
  }

function view_email_contents(contents, mailbox){

    fetch(`/emails/${contents["id"]}`)
    .then(response => response.json())
    .then(email_contents =>{

      console.log(contents);

      // Get contents of email and create element for it
      const emailcontents = document.createElement('div');
      emailcontents.className = "emailcontents";
      emailcontents.innerHTML = `<div>From: ${email_contents["sender"]} </div>`;
      emailcontents.innerHTML += `<div>To: ${email_contents["recipients"]} </div>`;
      emailcontents.innerHTML += `<div>Subject: ${email_contents["subject"]}</div>`;
      emailcontents.innerHTML += `<div>Timestamp: ${email_contents["timestamp"]}</div>`;
      emailcontents.innerHTML += "<div style='margin-bottom: 15px;'><button id = 'reply' class='btn btn-sm btn-outline-primary'>Reply</button></div>";
      emailcontents.innerHTML += '<hr>';
      emailcontents.innerHTML += `<div>${email_contents["body"]}</div>`;
      emailcontents.innerHTML += '<br>';

      // Add archive/unarchive button depending on archive property


      if (mailbox != 'sent' && email_contents["archived"]== false) {
      emailcontents.innerHTML += "<div><button id='archive' class='btn btn-sm btn-outline-primary'>Archive</button></div>";
      }
      else if (mailbox != 'sent' && email_contents["archived"]== true)
        {
        emailcontents.innerHTML += "<div><button id='archive' class='btn btn-sm btn-outline-primary'>Unarchive</button></div>";
      }

      emailcontents.style.display = "flex";
      emailcontents.style.flexDirection = "column";

       // Display email contents to user while hiding other views when email is clicked
      document.querySelectorAll('.email').forEach(email => {
        email.style.display = 'none';
      } )
      document.querySelector('h3').style.display = 'none';
      document.querySelector('#emails-view').append(emailcontents);
      document.querySelector('.emailcontents').style.display = 'block';

      // Add event listener to archive button
      if (mailbox != 'sent') {
        document.querySelector('#archive').addEventListener('click', function(){
            if (document.querySelector('#archive').innerHTML == 'Archive'){
              fetch(`/emails/${contents["id"]}`,{
              method: 'PUT',
              body: JSON.stringify({
                  archived: true
                    })
                  })
              .then(load_mailbox('inbox'))
                }
            else {
              fetch(`/emails/${contents["id"]}`,{
            method: 'PUT',
            body: JSON.stringify({
                archived: false
                  })
                })
              .then(load_mailbox('inbox'))
            }

        });
      }

      // Add event listener to reply button
      document.querySelector('#reply').addEventListener('click', () => reply_email(contents));

      });

      // Change read to true in emails
      fetch(`/emails/${contents["id"]}`, {
        method: 'PUT',
        body: JSON.stringify({
          read : true
          })
        })

    }

function reply_email(contents){
  // Redirect to compose form
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display ='block';
  console.log(contents);

  // Prefill form with recipient
  document.querySelector('#compose-recipients').value=`${contents["sender"]}`;

  //Prefill subject line
  if (contents["subject"].startsWith('Re:')) {
    document.querySelector('#compose-subject').value =`${contents["subject"]}`
  }
  else {
  document.querySelector('#compose-subject').value=`Re: ${contents["subject"]}`;
  }

  //Prefill body with past email
  document.querySelector('#compose-body').value = `On ${contents["timestamp"]} ${contents["sender"]} wrote : \n ${contents["body"]}\n `;


}





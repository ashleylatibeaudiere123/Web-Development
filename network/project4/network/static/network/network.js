
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.editlink').forEach(editlink =>
        {editlink.onclick = () => {
        // Get specific post corresponding to that id
            id = editlink.dataset.id;

            post = document.getElementById(id);

            if (editlink.innerHTML == "Edit"){

                // Edit that post
                edit(post);
            }
            else
            {
                // Save edited post to server and update it on screen using js
                save(post);
                editlink.innerHTML = "Edit";}
            }});
    document.querySelectorAll('.likes').forEach(likes =>{
        likes.onclick = () =>{
            // Find out which post the liked button is linked to
            id = likes.dataset.id;
            update_likes(id);
        }
    });

    });


function edit(post){

    // Select original post and link
    post_contents = post.querySelector('.postcontents');
    editlink = post.querySelector('.editlink');

    // Check if text area exists and if not create one
    post_edit_contents = post.querySelector('.editcontents');
    post_text_area = post_edit_contents.querySelector('.posttextarea');

    if (post_text_area == null) {
        //Make text area and append it
        post_text_area = document.createElement('textarea');
        post_text_area.className ='posttextarea';
        post_edit_contents.append(post_text_area);
    }

    // Make text area visible
    post_edit_contents.style.display = 'block';

    // Fill text area with original post
    post_text_area.value = post_contents.innerHTML;

    //Make original post section invisible
    post_contents.style.display ='none';


    // Change edit link text to save
    editlink.innerHTML = 'Save';

    // Assign same id to post text are
    post_text_area.id = editlink.dataset.id;

}

function save(post){
    // Obtain new post in text area
                post_text = post.querySelector('.posttextarea').value;
                actual_content = post_text;


                // Submit edits using fetch
                fetch(`/edit/${id}`, {
                    method: 'PUT',
                    headers:{
                        'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
                        'Content-Type':'application/json'
                    },
                    body: JSON.stringify({
                        post: actual_content
                    })
                })

                // Get response from server, separating its status and data
                .then(response => {
                    return response.json().then(data => ({
                    status: response.status,
                    data: data
                        }));
                    })
                .then(({status, data}) =>{

                    // Log status and data
                    console.log("Status:", status);
                    console.log("Data:", data);

                    //Make textarea disappear
                    textarea = post.querySelector('.editcontents');
                    textarea.style.display = 'none';

                    // Determine to edit post based on response
                    edited_post = post.querySelector('.postcontents');

                    if (status === 403 && data.error === "You cannot edit someone else's post.")
                    {
                        console.log(1);

                        // Reset post to the same

                        edited_post.innerHTML = data.post;
                    }
                    else {
                        // Update post

                        edited_post.innerHTML = actual_content;
                         }
                    edited_post.style.display= 'block';
                });

            }

function update_likes(id) {

            // Submit that the liked button was pressed
        fetch(`/likes/${id}`,{
                method:'PUT',
                headers:{
                    'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretokenlikes"]').value,
                    'Content-Type':'application/json'
                },
                body: JSON.stringify({
                    liked_button_pressed: true,
                })
            })
        .then(response => response.json())
        .then(result => {
                console.log(result);
                post = document.getElementById(id)
                likescount = post.querySelector('.likescount');
                likescount.innerHTML = parseInt(result["likes"]);

            });
}

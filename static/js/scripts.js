$(document).ready(function(){

    $('#add-data').click(function(){
        $('.add-det').addClass('popup');
    });
    
    $('.add-det form .fa-times').click(function(){
        $('.add-det').removeClass('popup');
    });

    $('#signup-data').click(function(){
        $('.signup-form').addClass('popup');
    });
    
    $('.signup-form form .fa-times').click(function(){
        $('.signup-form').removeClass('popup');
    });

    $('#adsignup-data').click(function(){
        $('.adsignup-form').addClass('popup');
    });
    
    $('.adsignup-form form .fa-times').click(function(){
        $('.adsignup-form').removeClass('popup');
    });

});

// Function to handle signup
function handleSignup($form, signupUrl) {
    var $error = $form.find(".error");
    var $successMessage = $("#success-message");
    var data = $form.serialize();

    $.ajax({
        url: signupUrl,
        type: "POST",
        data: data,
        dataType: "json",
        success: function (resp) {
            // Update success message
            $successMessage.text("Successfully Registered!");

            // Clear form fields
            $form.find('input[type=text], input[type=email], input[type=password]').val('');

            // Show the form for a custom modal
            $form.closest('.adsignup-form').toggle();
            $form.closest('.signup-form').toggle();

            // Fetch updated data and refresh the table
            fetchAllData();
        },
        error: function (resp) {
            $error.text(resp.responseJSON.error).removeClass("error--hidden");
        }
    });
}

// User signup
$("form[name=signup_form]").submit(function (e) {
    handleSignup($(this), "/user/signup");
    e.preventDefault();
});

// Admin signup
$("form[name=adsignup_form]").submit(function (e) {
    handleSignup($(this), "/user/adsignup");
    e.preventDefault();
});



document.addEventListener("DOMContentLoaded", function() {
    const sections = document.querySelectorAll("section"); // Select all sections
    const navLinks = document.querySelectorAll(".navbar a"); // Select all navigation links
    
    // Function to hide all sections except the specified one
    function showSection(sectionId) {
        sections.forEach(section => {
            if (section.id === sectionId) {
                section.style.display = "block";
            } else {
                section.style.display = "none";
            }
        });
    }
    // Event listener for navigation clicks
    navLinks.forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault(); // Prevent the default anchor behavior

            const sectionId = this.getAttribute("data-section"); // Get the section ID from data attribute
            showSection(sectionId); // Show the clicked section
        });
    });
});



// student record
function updateDisplay() {
    var selectedClass = document.getElementById("classDropdown").value;
    fetch(`/get_class_data/${selectedClass}`)
        .then(response => response.json())
        .then(data => {
            var classData = data.map((student, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td>${student.fname}</td>
                    <td>${student.lname}</td>
                    <td>${student.roll_no}</td>
                    <td>${student.height}</td>
                    <td>${student.weight}</td>
                    <td>${student.bmi}</td>
                </tr>
            `).join("\n");
            document.getElementById("studentListBody").innerHTML = classData || `<tr><td colspan="7">No data available for ${selectedClass}</td></tr>`;
        });
}

function addStudentFromForm() {
    var firstName = document.forms["add_det"]["fname"].value;
    var lastName = document.forms["add_det"]["lname"].value;
    var roll_no = document.forms["add_det"]["roll_no"].value;
    var height = parseFloat(document.forms["add_det"]["height"].value);
    var weight = parseFloat(document.forms["add_det"]["weight"].value);
    var selectedClass = document.getElementById("classDropdown").value;
    
    // Fetch school name from the hidden input
    var school_name = document.getElementById("schoolName").value;

    addStudent(firstName, lastName, roll_no, height, weight, selectedClass, school_name);
    generate_qr(firstName, roll_no, selectedClass, school_name);

    // Clear and close the form after saving details
    document.getElementById('addDetForm').reset();
    closeForm();

    return false;
}


function addStudent(fname, lname, roll_no, height, weight, selectedClass, school_name) {
    fetch('/add_student', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            fname: fname,
            lname: lname,
            roll_no: roll_no,
            height: height,
            weight: weight,
            studentClass: selectedClass,
            school_name: school_name // Add school_name to the request
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        updateDisplay();
        closeForm();
    });
}

function generate_qr(fname, roll_no, selectedClass, school_name) {
    fetch('/generate_id_card', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            fname: fname,
            roll_no: roll_no,
            studentClass: selectedClass,
            school_name: school_name // Add school_name to the request
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    });
}




// student attend
document.addEventListener('DOMContentLoaded', function () {
    async function fetchAttendanceStatistics() {
        try {
            const response = await fetch('/attendance-statistics/<school_name>/<student_class>');
            if (!response.ok) {
                throw new Error('Failed to fetch attendance statistics');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching attendance statistics:', error);
            throw error;
        }
    }

    async function generateRows() {
        const statistics = await fetchAttendanceStatistics();
        const tbody = document.getElementById('studentRecordBody');

        if (statistics) {
            let rowNumber = 1;

            statistics.school_details.forEach(school => {
                school.class_details.forEach(studentClass => {
                    const row = tbody.insertRow();
                    row.id = `row-${studentClass.class_name}`;

                    const cells = [
                        row.insertCell(0),
                        row.insertCell(1),
                        row.insertCell(2),
                        row.insertCell(3),
                        row.insertCell(4),
                        row.insertCell(5)
                    ];

                    cells[0].textContent = `${rowNumber}.`;
                    cells[1].textContent = studentClass.class_name;
                    cells[2].textContent = studentClass.present_count;
                    cells[3].textContent = studentClass.absent_count;

                    const uploadContainer = document.createElement('div');
                    uploadContainer.className = 'upload-container';

                    const form = document.createElement('form');
                    form.id = `student-upload-form-${studentClass.class_name}`;
                    form.enctype = 'multipart/form-data';

                    const input = document.createElement('input');
                    input.type = 'file';
                    input.id = `student-upload-input-${studentClass.class_name}`;
                    input.accept = '.jpg';

                    const button = document.createElement('button');
                    button.type = 'submit';
                    button.id = `student-upload-btn-${studentClass.class_name}`;
                    button.textContent = 'Upload';

                    form.appendChild(input);
                    form.appendChild(button);
                    uploadContainer.appendChild(form);

                    cells[4].appendChild(uploadContainer);

                    const uploadedFileContainer = document.createElement('div');
                    uploadedFileContainer.className = 'uploaded-file';

                    const uploadedImage = document.createElement('img');
                    uploadedImage.id = `student-uploaded-image-${studentClass.class_name}`;
                    uploadedImage.src = `data:image/jpeg;base64,${studentClass.image_data}`; // Modify here
                    uploadedImage.alt = 'Uploaded Image';

                    uploadedFileContainer.appendChild(uploadedImage);
                    cells[5].appendChild(uploadedFileContainer);

                    // Add event listener for file upload
                    form.addEventListener('submit', function (event) {
                        event.preventDefault();
                        uploadImage(school.school_name, studentClass.class_name);
                    });

                    rowNumber++;
                });
            });
        }
    }


    async function uploadImage(school_name, class_name) {
        const fileInput = document.getElementById(`student-upload-input-${class_name}`);
        const file = fileInput.files[0];
    
        if (!file) {
            console.error('No file selected');
            return;
        }
    
        const formData = new FormData();
        formData.append('file', file);
    
        try {
            const response = await fetch(`/upload-image/${school_name}/${class_name}`, {
                method: 'POST',
                body: formData
            });
    
            if (!response.ok) {
                throw new Error('File upload failed');
            }
    
            const result = await response.json();
            console.log(result);
    
            // Access correct image data key returned by the server
            const image_data = result.stu_image_data;
    
            // Update the uploaded image src attribute
            document.getElementById(`student-uploaded-image-${class_name}`).src = `data:image/jpeg;base64,${image_data}`;
    
            // Provide feedback to the user on successful upload (e.g., display a success message)
            alert('File uploaded successfully');
        } catch (error) {
            console.error('Error uploading file:', error);
            // Provide feedback to the user on upload failure (e.g., display an error message)
            alert('File upload failed');
        }
    }
    

    generateRows();
});

//  ---------------------------------------------------------------------------------------------------------

// Admin Part Start

// User Section

// Function to fetch data for user
async function fetchUserData() {
    try {
        const response = await fetch('/fetch-all-data');  // Adjust the route to match your Flask endpoint for user data
        const data = await response.json();

        // Get the table body
        const tbody = document.getElementById('user-data-body');

        // Clear existing rows
        tbody.innerHTML = '';

        let index = -1

        // Loop through the array of documents and create a row for each
        data.forEach(doc => {
            // Create a new row and cells for user data
            const row = document.createElement('tr');
            const idUCell = document.createElement('td');
            const nameUCell = document.createElement('td');
            const schoolUCell = document.createElement('td');
            const emailUCell = document.createElement('td');
            const actionUCell = document.createElement('td');
            const updatePasswordUButton = document.createElement('button');
            const deleteUserUButton = document.createElement('button');

            index++;

            // Set the cell values
            idUCell.textContent = index + 1;
            nameUCell.textContent = doc.name;
            schoolUCell.textContent = doc.school;
            emailUCell.textContent = doc.email;

            // Set button properties
            updatePasswordUButton.textContent = 'Update Password';
            updatePasswordUButton.addEventListener('click', () => confirmUpdatePassword(doc.school));

            deleteUserUButton.textContent = 'Delete User';
            deleteUserUButton.addEventListener('click', () => confirmDeleteUser(doc.school));

            // Append cells to the row
            row.appendChild(idUCell);
            row.appendChild(nameUCell);
            row.appendChild(schoolUCell);
            row.appendChild(emailUCell);
            actionUCell.appendChild(updatePasswordUButton);
            actionUCell.appendChild(deleteUserUButton);
            row.appendChild(actionUCell);

            // Append the row to the table body
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching user data:', error);
    }
}

// Call the fetchUserData function when the page loads
document.addEventListener('DOMContentLoaded', fetchUserData);

// Function to confirm updating the password for a user
function confirmUpdatePassword(school) {
    const confirmation = confirm(`Do you want to update the password for the user '${school}'?`);
    if (confirmation) {
        updatePassword(school);
        clearTableRow(school);
    }
}

function confirmDeleteUser(school) {
    const confirmation = confirm(`Do you want to delete the user '${school}'?`);
    if (confirmation) {
        deleteUser(school);
        clearTableRow(school);
    }
}

function clearTableRow(school) {
    const row = document.getElementById(`row-${school}`);
    row.remove();
}


// Function to update the password for a user
async function updatePassword(school) {
    try {
        const newPasswordU = prompt('Enter the new password:');
        if (newPasswordU) {
            const response = await fetch(`/update-password/${school}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ new_password: newPasswordU }),
            });

            const result = await response.json();
            alert(result.message || result.error);
            fetchUserData();
        }
    } catch (error) {
        console.error('Error updating password:', error);
    }
}

// Function to delete a user
async function deleteUser(school) {
    try {
        const response = await fetch(`/delete-user/${school}`, {
            method: 'DELETE',
        });

        const result = await response.json();
        alert(result.message || result.error);
        fetchUserData();
    } catch (error) {
        console.error('Error deleting user:', error);
    }
}
// Call the fetchAllData function when the page loads
document.addEventListener('DOMContentLoaded', fetchAllData);




// Admin Section

// Function to fetch all data from the API and populate the table body
async function fetchAllData() {
    try {
        const response = await fetch('/admin-data');
        const data = await response.json();

        // Get the table body
        const tbody = document.getElementById('ad-body');

        // Clear existing rows
        tbody.innerHTML = '';

        let index = -1

        // Loop through the array of documents and create a row for each
        data.forEach(doc => {
            // Create a new row and cells
            const row = document.createElement('tr');
            const idCell = document.createElement('td');
            const nameCell = document.createElement('td');
            const usernameCell = document.createElement('td');
            const emailCell = document.createElement('td');
            const actionCell = document.createElement('td');
            const updatePassadButton = document.createElement('button');
            const deleteAdminButton = document.createElement('button');

            index++;

            // Set the cell values
            idCell.textContent = index + 1;
            nameCell.textContent = doc.name;
            usernameCell.textContent = doc.username;
            emailCell.textContent = doc.email;
          
            // Set button properties
            updatePassadButton.textContent = 'Update Password';
            updatePassadButton.addEventListener('click', () => confirmUpdatePassad(doc.username));

            deleteAdminButton.textContent = 'Delete User';
            deleteAdminButton.addEventListener('click', () => confirmDeleteAdmin(doc.username));

            // Append cells to the row
            row.appendChild(idCell);
            row.appendChild(nameCell);
            row.appendChild(usernameCell);
            row.appendChild(emailCell);
            actionCell.appendChild(updatePassadButton);
            actionCell.appendChild(deleteAdminButton);
            row.appendChild(actionCell);

            // Append the row to the table body
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Function to confirm updating the password for a user
function confirmUpdatePassad(username) {
    const confirmation = confirm(`Do you want to update the password for the user '${username}'?`);
    if (confirmation) {
        updatePassad(username);
        clearTableRow(username);
    }
}

function confirmDeleteAdmin(username) {
    const confirmation = confirm(`Do you want to delete the user '${username}'?`);
    if (confirmation) {
        deleteAdmin(username);
        clearTableRow(username);
    }
}

function clearTableRow(username) {
    const row = document.getElementById(`row-${username}`);
    row.remove();
}


// Function to update the password for a user
async function updatePassad(username) {
    try {
        const newPassword = prompt('Enter the new password:');
        if (newPassword) {
            const response = await fetch(`/admin-upd-pass/${username}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ new_password: newPassword }),
            });

            const result = await response.json();
            alert(result.message || result.error);
            fetchAllData();
        }
    } catch (error) {
        console.error('Error updating password:', error);
    }
}

// Function to delete a user
async function deleteAdmin(username) {
    try {
        const response = await fetch(`/admin-del/${username}`, {
            method: 'DELETE',
        });

        const result = await response.json();
        alert(result.message || result.error);
        fetchAllData();
    } catch (error) {
        console.error('Error deleting user:', error);
    }
}

// Call the fetchAllData function when the page loads
document.addEventListener('DOMContentLoaded', fetchAllData);


// Report Section


$(document).ready(function(){
    $("#maharashtraArea").click(function(e){
        e.preventDefault(); // Prevents the default behavior of the link (if href is present)
        e.stopPropagation(); // Stops the event from propagating to parent elements

        // Toggle the visibility of the dropdown box associated with Maharashtra
        $("#maharashtraDropdown").toggle();

        // Hide other dropdown boxes if they are visible
        $(".dropdown-container").not("#maharashtraDropdown").hide();
    });

    // Close dropdown boxes if user clicks outside of them
    $(document).click(function(){
        $(".dropdown-container").hide();
    });

    // Prevent hiding the dropdown box when clicking inside it
    $("#maharashtraDropdown").click(function(e){
        e.stopPropagation();
    });
});



// Your Maharashtra districts data
var districts = [
    "Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana",
    "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna",
    "Kolhapur", "Latur", "Mumbai", "Mumbai Suburban", "Nagpur", "Nanded",
    "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad",
    "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha",
    "Washim", "Yavatmal"
];

$(document).ready(function() {
    // Attach event handler to the district dropdown
    $("#district").on("change", function() {
        // Show or hide the schools-data div based on dropdown selection
        if ($(this).val() !== "") {
            $("#schools-data").show();
            fetchDistrictData();
        } else {
            $("#schools-data").hide();
        }
    });
});

function fetchDistrictData() {
    var selectedDistrict = $("#district").val();

    // Make an AJAX request to the Flask route
    $.ajax({
        url: '/fetch-district/' + selectedDistrict,
        type: 'GET',
        success: function(data) {
            // Handle the fetched data
            displayFetchedData(data);
        },
        error: function(error) {
            console.error('Error fetching district data:', error);

            // Update an element with an error message or display an alert
            $(".schoolListBody").html('<tr><td colspan="5">Error fetching data. Please try again later.</td></tr>');
        }
    });
}

function displayFetchedData(data) {
    // Clear previous results
    $(".schoolListBody").empty();

    // Check for errors
    if (data.error) {
        $(".schoolListBody").html('<tr><td colspan="5">Error: ' + data.error + '</td></tr>');
    } else {
        // Display fetched data
        for (var i = 0; i < data.length; i++) {
            var user = data[i];
            var html = '<tr>';
            html += '<td>' + (i + 1) + '</td>';
            html += '<td>' + (user.school || 'N/A') + '</td>';
            html += '<td>' + (user.email || 'N/A') + '</td>';
            html += '<td>' + (user.district || 'N/A') + '</td>';
            html += '<td><input type="date" id="reportDate_' + i + '"></td>';
            html += '<td><a href="#" onclick="viewReport(\'' + user.school + '\', \'' + i + '\')">View Report</a></td>';
            html += '</tr>';
            $(".schoolListBody").append(html);
        }
    }
}


// Function to handle "View Report" click
function viewReport(schoolName, rowIndex) {
    var selectedDate = $("#reportDate_" + rowIndex).val();

    // Make an AJAX request to fetch the report data based on the selected date
    $.ajax({
        url: '/fetch-report/' + schoolName + '/' + selectedDate,
        type: 'GET',
        success: function() {

            // Trigger PDF download after displaying report data
            downloadPDF(schoolName, selectedDate);
        },
        error: function(error) {
            console.error('Error fetching report data:', error);
            // Display an error message or take appropriate action
        }
    });
}

function downloadPDF(schoolName, selectedDate) {
    // Make an AJAX request to download the PDF
    $.ajax({
        url: '/download-pdf/' + schoolName + '/' + selectedDate,
        type: 'GET',
        xhrFields: {
            responseType: 'blob'  // Set the expected response type to 'blob'
        },
        success: function(response) {
            // Create a Blob from the response
            var blob = new Blob([response], { type: 'application/pdf' });

            // Create a URL for the Blob
            var url = window.URL.createObjectURL(blob);

            // Create a link element and trigger a click event to initiate download
            var link = document.createElement('a');
            link.href = url;
            link.download = `${schoolName}-${selectedDate}.pdf`;
            document.body.appendChild(link);
            link.click();

            // Clean up
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        },
        error: function(error) {
            console.error('Error downloading PDF:', error);
            // Display an error message or take appropriate action
        }
    });
}

function decodeBase64Image(encodedImage) {
    var binary = atob(encodedImage.split(',')[1]);
    var array = [];
    for (var i = 0; i < binary.length; i++) {
        array.push(binary.charCodeAt(i));
    }
    return new Uint8Array(array);
}
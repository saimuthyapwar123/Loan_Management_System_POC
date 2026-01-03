async function loadProfile() {
    const res = await fetch("http://127.0.0.1:8000/loan_auth/auth/me", {
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        }
    });

    if (!res.ok) {
        document.getElementById("profileBox").innerText = "Unable to load profile";
        return;
    }

    const data = await res.json();

    document.getElementById("profileBox").innerHTML = `
    <h2 class="profile-title">My Profile</h2>
    <hr class="profile-divider">

    <p><b>Name :</b> ${data.first_name} ${data.last_name}</p>
    <p><b>DOB :</b> ${data.dob}</p>
    <p><b>Email :</b> ${data.email || "N/A"}</p>
    <p><b>Aadhaar :</b> ${data.aadhar_number}</p>
`;

}

loadProfile();

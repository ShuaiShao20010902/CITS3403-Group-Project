function toggleUserInfo(btn){
    const box  = document.getElementById('user-info');
    const open = box.style.display !== 'block';

    box.style.display = open ? 'block' : 'none';
    btn.innerText     = open 
        ? 'Hide User Info ▲' 
        : 'Add User Info (Optional) ▼';
}
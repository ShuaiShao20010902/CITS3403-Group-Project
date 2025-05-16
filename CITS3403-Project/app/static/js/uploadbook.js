function toggleUserInfo(btn){
    const box  = document.getElementById('user-info');
    const open = box.style.display !== 'block';

    box.style.display = open ? 'block' : 'none';
    btn.innerText     = open 
        ? 'Hide User Info ▲' 
        : 'Add User Info (Optional) ▼';
}

document.addEventListener('DOMContentLoaded', () => {
    const hidden = document.getElementById('completed-field');
    const btn    = document.getElementById('toggle-completed');

    btn.addEventListener('click', () => {
      const newDone = !(hidden.value === 'True' || hidden.value === 'true');
      hidden.value = newDone.toString();
      btn.textContent = newDone
        ? 'Mark as Incomplete ❌'
        : 'Mark as Complete ✅';
      btn.classList.toggle('complete', newDone);
    });
  });
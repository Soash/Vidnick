const toggle = document.getElementById('toggle');
      const learnerContent = document.getElementById('learnerContent');
      const expertContent = document.getElementById('expertContent');
  
      toggle.addEventListener('change', function() {
        if (this.checked) {
          learnerContent.classList.add('hidden');
          expertContent.classList.remove('hidden');
        } else {
          learnerContent.classList.remove('hidden');
          expertContent.classList.add('hidden');
        }
      });
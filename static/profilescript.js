document.addEventListener('DOMContentLoaded', function() {
    const editButton = document.querySelector('.edit-button');
    const profileForm = document.querySelector('.edit-profile');
    const backButton = document.querySelector('.back-button');
    const modal = document.getElementById("myModal");
    const modalImg = document.getElementById("modalImg");

    profileForm.style.display = 'none';
    backButton.style.display = 'none';

    editButton.addEventListener('click', function() {
        profileForm.style.display = 'block';
        backButton.style.display = 'inline-block';
        editButton.style.display = 'none';
    });

    const avatarInput = document.querySelector('input[name="avatar"]');
    const avatarPreview = document.querySelector('.profile-info img');

    avatarInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function() {
                avatarPreview.src = reader.result;
            }
            reader.readAsDataURL(file);
        }
    });

    // Обработчик события клика на изображении для открытия в модальном окне
    document.querySelectorAll('img').forEach(image => {
        image.addEventListener('click', function() {
            modal.style.display = "block";

            // Определение размеров экрана
            const screenWidth = window.innerWidth;
            const screenHeight = window.innerHeight;

            // Вычисление размеров изображения в зависимости от размеров экрана
            const maxImageWidth = screenWidth * 0.8;
            const maxImageHeight = screenHeight * 0.8;

            // Установка размеров изображения
            modalImg.style.maxWidth = maxImageWidth + 'px';
            modalImg.style.maxHeight = maxImageHeight + 'px';

            modalImg.src = this.src;
        });
    });

    const span = document.getElementsByClassName("close")[0];
    span.onclick = function() {
        modal.style.display = "none";
    }

    // Обновление кнопок подписки
    const subscribeButton = document.querySelector('.subscribe-button');
    const unsubscribeButton = document.querySelector('.unsubscribe-button');

    if (subscribeButton && unsubscribeButton) {
        subscribeButton.addEventListener('click', function() {
            subscribeButton.style.display = 'none';
            unsubscribeButton.style.display = 'block';
        });

        unsubscribeButton.addEventListener('click', function() {
            unsubscribeButton.style.display = 'none';
            subscribeButton.style.display = 'block';
        });
    }
});

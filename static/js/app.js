let mainCatalogSwiper = new Swiper(".main-catalog__swiper", {
  slidesPerView: 'auto',
  spaceBetween: 20,
  autoplay: {
    delay: 3000,
  },
  breakpoints: {
    320: {
      slidesPerView: 1.3,
      spaceBetween: 20,
    },
    640: {
      slidesPerView: 1.8,
      spaceBetween: 25,
    },
    768: {
      slidesPerView: 2.5,
      spaceBetween: 30,
    },
    1024: {
      slidesPerView: 3.5,
      spaceBetween: 35,
    },
    1280: {
      slidesPerView: 4,
      spaceBetween: 44,
    }
  },
});

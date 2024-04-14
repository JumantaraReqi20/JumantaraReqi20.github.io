$(function() {
    $.get('/data/data.json', function(obj) {
      var str = "";
      $.each(obj, function(n, data) {
        str += "<tr>";
        str += "<td>" + (n + 1) + "</td>";
        str += "<td id='news-title'>" + data['judul'] + "</td>";
        str += "<td>" + data['kategori'] + "</td>";
        str += "<td id='news-time'>" + data['waktu_publish'].replace(/\n/g, "<br>") + "</td>";
        str += "<td id='news-time'>" + data['waktu_scraping'].replace(/\n/g, "<br>") + "</td>";
        str += "</tr>";
      });
      $('#news-table tbody').html(str);
    });
  });
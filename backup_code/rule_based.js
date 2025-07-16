function getValue(cardValue) {
  return +cardValue.substring(4, 6);
}

const rank = {
  coc: "coc",
  doi: "doi",
  sanh: "sanh",
  bacay: "xamco",
  tuqui: "tuqui",
  badoithong: "3doithong",
  bondoithong: "4doithong",
  namdoithong: "5doithong",
  saudoithong: "6doithong",
  heo: "heo",
  doiheo: "doiheo",
  baheo: "baheo",
  khonghople: "khonghople",
  hople: "hople",
};

const card = {
  A: 14,
  K: 13,
  Q: 12,
  J: 11,
  10: 10,
  9: 9,
  8: 8,
  7: 7,
  6: 6,
  5: 5,
  4: 4,
  3: 3,
  2: 16,
};

function chuyenchuoi(a) {
  g = [];

  for (var i = 0; i < a.length; i++) {
    g.push(getValue(a[i])); //substring cat chuoi
  }
  return g;
}

function sortNumberAsc(a, b) {
  return a - b;
}

function ktrasanh(data) {
  var v = [];
  v = chuyenchuoi(data);
  v.sort(sortNumberAsc); //sap xep mang tang dan

  for (var i = 0; i < v.length - 1; i++) {
    if (v[i] + 1 == v[i + 1]) {
      t = 0;
    } else {
      t = 1;
      break;
    }
  }
  return t;
}

function ktradoithong(data) {
  var v = [];
  v = chuyenchuoi(data);

  v.sort(sortNumberAsc); //sap xep mang tang dan

  for (var i = 0; i < v.length - 2; i += 2) {
    if (v[i] == v[i + 1] && v[i] + 1 == v[i + 2]) {
      //kiem tra ex: 1,2,3,4,5...
      t = 0;
    } else {
      t = 1;
      break;
    }
  }
  return t;
}

function kiemtrahople(data) {
  dem = data.length;
  var g = "";
  if (dem == 1 && data != "") {
    g = rank.coc;
  } else if (dem == 2) {
    c1 = getValue(data[0]);
    c2 = getValue(data[1]);
    if (c1 == c2) {
      g = rank.doi;
    } else {
      g = rank.khonghople;
    }
  } else if (dem > 2) {
    if (ktrasanh(data) == 0) {
      g = "sanh";
    } else {
      if (dem == 3) {
        c1 = getValue(data[0]);
        c2 = getValue(data[1]);
        c3 = getValue(data[2]);
        if (c1 == c2 && c2 == c3) {
          g = rank.bacay;
        } else {
          g = rank.khonghople;
        }
      } else if (dem == 4) {
        c1 = getValue(data[0]);
        c2 = getValue(data[1]);
        c3 = getValue(data[2]);
        c4 = getValue(data[3]);
        if (c1 == c2 && c1 == c3 && c1 == c4) {
          g = rank.tuqui;
        } else {
          g = rank.khonghople;
        }
      } else if (dem == 6) {
        if (ktradoithong(data) == 0) {
          g = rank.badoithong;
        } else {
          g = rank.khonghople;
        }
      } else if (dem == 8) {
        if (ktradoithong(data) == 0) {
          g = rank;
        } else {
          g = rank.khonghople;
        }
      } else if (dem == 10) {
        if (ktradoithong(data) == 0) {
          g = rank.namdoithong;
        } else {
          g = rank.khonghople;
        }
      } else if (dem == 12) {
        if (ktradoithong(data) == 0) {
          g = rank.saudoithong;
        } else {
          g = rank.khonghople;
        }
      } else {
        g = rank.khonghople;
      }
    }
  }
  return g;
}

function hoanvi_all(a) {
  var tam = 0;
  for (var i = 0; i < a.length - 1; i++) {
    dt1 = a[i].substring(4, 6);
    dt2 = a[i].substring(6, 7);
    dt3 = a[i + 1].substring(4, 6);
    dt4 = a[i + 1].substring(6, 7);
    if (dt2 == "a") {
      dt2 = 0.1;
    } else if (dt2 == "b") {
      dt2 = 0.2;
    } else if (dt2 == "c") {
      dt2 = 0.3;
    } else if (dt2 == "d") {
      dt2 = 0.4;
    }

    if (dt4 == "a") {
      dt4 = 0.1;
    } else if (dt4 == "b") {
      dt4 = 0.2;
    } else if (dt4 == "c") {
      dt4 = 0.3;
    } else if (dt4 == "d") {
      dt4 = 0.4;
    }
    if (dt1 + dt2 > dt3 + dt4) {
      tam = a[i];
      a[i] = a[i + 1];
      a[i + 1] = tam;
    }
  }
  return a;
}
function trung_lap(a) {
  var seen = {};
  return a.filter(function (item) {
    return seen.hasOwnProperty(item) ? false : (seen[item] = true);
  });
}
function giaomang(a, b) {
  var c = [];
  if (a != "") {
    for (var i = 0; i < a.length; i++) {
      c.push(a[i]);
    }
  }
  if (b != "" && a != "") {
    for (var i = 0; i < b.length; i++) {
      if (c.indexOf(b[i]) >= 0) {
        c.splice(c.indexOf(b[i]), 1);
      }
    }
  } else if (b == "" && a != "") {
    c = a;
  } else if (a == "" && b != "") {
    c = b;
  }
  return c;
}
///////////////////////////////////////////////////////////////
function hv_bai_lon(a) {
  //ex: 3a,3b,3c,4a,5a ==>3b,3c,3a,4a,5a

  var tam = "";
  for (var i = 0; i < a.length - 1; i++) {
    if (a[i].substring(4, 6) == a[i + 1].substring(4, 6)) {
      tam = a[i];
      a[i] = a[i + 1];
      a[i + 1] = tam;
    }
  }
  return a;
}
////////////////////////////////////////////////////////
function AI_d_danh_d_2c(o, a) {
  var a1 = a;
  var doi2 = AIktra_doi(o);

  var doi_thong = AIktra_doithong(doi2);

  var tu_qui = AIktra_tuqui(o);
  var sanh = AIktra_sanh(hv_bai_lon(o));
  var danh = [];
  var doi1 = giaomang(o, sanh);
  var doi = AIktra_doi(hoanvi_all(doi1));

  for (var i = 0; i < doi.length - 1; i += 2) {
    if (doi_thong.indexOf(doi[i]) < 0 && doi_thong.indexOf(doi[i + 1]) < 0) {
      if (
        parseInt(doi[i].substring(4, 6)) >
          parseInt(a1[a1.length - 1].substring(4, 6)) &&
        tu_qui.indexOf(doi[i]) < 0
      ) {
        danh.push(doi[i]);
        danh.push(doi[i + 1]);
        break;
      } else if (
        parseInt(doi[i].substring(4, 6)) ==
          parseInt(a1[a1.length - 1].substring(4, 6)) &&
        tu_qui.indexOf(doi[i]) < 0
      ) {
        var dt2 = doi[i + 1].substring(6, 7);
        var dt3 = a1[a1.length - 1].substring(6, 7);
        if (dt2 == "a") {
          dt2 = 0.1;
        } else if (dt2 == "b") {
          dt2 = 0.2;
        } else if (dt2 == "c") {
          dt2 = 0.3;
        } else if (dt2 == "d") {
          dt2 = 0.4;
        }
        ///////////////////////
        if (dt3 == "a") {
          dt3 = 0.1;
        } else if (dt3 == "b") {
          dt3 = 0.2;
        } else if (dt3 == "c") {
          dt3 = 0.3;
        } else if (dt3 == "d") {
          dt3 = 0.4;
        }
        if (dt2 > dt3) {
          danh = [];
          danh.push(doi[i]);
          danh.push(doi[i + 1]);
          break;
        }
      }
    }
  }
  //alert(danh);
  return danh;
}
function AI_c_danh_c_1c(a, b) {
  var danh = [];
  if (a != "") {
    for (var i = 0; i < a.length; i++) {
      if (a[i].substring(4, 6) > b[0].substring(4, 6)) {
        danh.push(a[i]);
        break;
      } else if (a[i].substring(4, 6) == b[0].substring(4, 6)) {
        var dt2 = a[i].substring(6, 7);
        var dt3 = b[0].substring(6, 7);
        if (dt2 == "a") {
          dt2 = 0.1;
        } else if (dt2 == "b") {
          dt2 = 0.2;
        } else if (dt2 == "c") {
          dt2 = 0.3;
        } else if (dt2 == "d") {
          dt2 = 0.4;
        }
        ///////////////////////
        if (dt3 == "a") {
          dt3 = 0.1;
        } else if (dt3 == "b") {
          dt3 = 0.2;
        } else if (dt3 == "c") {
          dt3 = 0.3;
        } else if (dt3 == "d") {
          dt3 = 0.4;
        }

        if (dt2 > dt3) {
          danh.push(a[i]);
          break;
        }
      }
    }
  }

  return danh;
}
function AI_xc_danh_xc_3c(a, b) {
  var danh = [];
  if (a != "") {
    for (
      var i = 0;
      i < a.length;
      i += 3 //333,444
    ) {
      if (a[i].substring(4, 6) > b[0].substring(4, 6)) {
        danh.push(a[i]);
        danh.push(a[i + 1]);
        danh.push(a[i + 2]);
        break;
      }
    }
  }
  return danh;
}
function AI_tq_danh_tq_4c(a, b) {
  var danh = [];
  for (var i = 0; i < a.length - 1; i++) {
    if (a[i].substring(4, 6) > b[0].substring(4, 6)) {
      danh.push(a[i]);
      danh.push(a[i + 1]);
      danh.push(a[i + 2]);
      danh.push(a[i + 3]);
      break;
    } else if (a[i].substring(4, 6) < b[0].substring(4, 6) && a.length > 4) {
      i = i + 3;
    }
  }
  return danh;
}
function AI_loc_danh_tung_pt(a, b) {
  var kq = [];
  if (b == "doi") {
    kq.push(a[0]);
    kq.push(a[1]);
  } else if (b == "xamco") {
    kq.push(a[0]);
    kq.push(a[1]);
    kq.push(a[2]);
  } else if (b == "tuqui") {
    kq.push(a[0]);
    kq.push(a[1]);
    kq.push(a[2]);
    kq.push(a[3]);
  } else if (b == "sanh") {
    for (var i = 0; i < a.length - 1; i++) {
      if (
        parseInt(a[i].substring(4, 6)) + 1 ==
        parseInt(a[i + 1].substring(4, 6))
      ) {
        if (kq == "") {
          kq.push(a[i]);
          kq.push(a[i + 1]);
        } else {
          kq.push(a[i + 1]);
        }
      } else {
        var e = a.length - kq.length; //danh sanh nhieu nhat truoc
        if (e > kq.length) {
          kq = [];
        } else break;
      }
    }
  } else if (b == "coc") {
    kq.push(a[0]);
  }
  return kq;
}
////////////////////////////////////////////////////////////////
function AI_tancong(o) {
  var doi = AIktra_doi(o);

  var doi_thong = AIktra_doithong(doi);
  var xam_co = AIktra_xamco(o);
  var tu_qui = AIktra_tuqui(o);

  var sanh = AIktra_sanh(hv_bai_lon(o));
  var danh = [],
    y1 = "",
    y2 = "",
    y3 = "",
    y4 = "",
    y5 = "";

  if (doi != "") {
    danh = [];
    danh = AI_loc_danh_tung_pt(doi, "doi");
    y3 = "doi";
  }
  if (xam_co != "") {
    danh = [];
    danh = AI_loc_danh_tung_pt(xam_co, "xamco");
    y4 = "xamco";
  }
  if (sanh != "") {
    danh = [];
    danh = AI_loc_danh_tung_pt(sanh, "sanh");
    y5 = "sanh";
  }
  if (tu_qui != "") {
    danh = AI_loc_danh_tung_pt(tu_qui, "tuqui");
    y1 = "tuqui";
  }
  if (doi_thong != "") {
    danh = [];
    danh = doi_thong;
    y2 = "doithong";
  }

  var coc = [];
  if (y1 == "tuqui") {
    coc = giaomang(o, tu_qui);
  }
  if (y2 == "doithong") {
    coc = giaomang(o, doi_thong);
  }

  coc = giaomang(o, sanh);

  var xamco1 = AIktra_xamco(coc);
  var xamco2 = giaomang(coc, xamco1);
  var doi1 = AIktra_doi(xamco2);
  var doi2 = giaomang(xamco2, doi1);

  if (doi2.length > 1) {
    danh = [];

    danh = AI_loc_danh_tung_pt(doi2, "coc");
  } else if (doi2.length == 1 && o.length == 1) {
    danh = [];
    danh = AI_loc_danh_tung_pt(doi2, "coc");
  } else if (tu_qui.length != 0) {
    danh = [];
    danh = AI_loc_danh_tung_pt(tu_qui, "tuqui");
  } else if (doi_thong.length != 0) {
    danh = [];
    danh = doi_thong;
  } else if (sanh.length != 0) {
    danh = [];
    danh = AI_loc_danh_tung_pt(sanh, "sanh");
  }

  return danh;
}
////////////////////////////////////////////////////////////
function AIktra_doi(x1) {
  //doi

  function in_of(a) {
    var b = [];
    for (var i = 0; i < a.length; i++) {
      b.push(a[i].substring(4, 6));
    }
    return b;
  }

  var a1 = [],
    a2 = [],
    a3 = [];

  for (
    var i = 0;
    i < x1.length - 1;
    i++ //3344455
  ) {
    if (x1[i].substring(4, 6) == x1[i + 1].substring(4, 6)) {
      if (a1 != "") {
        a2 = in_of(a1);
        if (a2.indexOf(x1[i].substring(4, 6)) < 0) {
          a1.push(x1[i]);
          a1.push(x1[i + 1]);
        }
      } else {
        a1.push(x1[i]);
        a1.push(x1[i + 1]);
      }
    }
  }
  //  alert(a1);
  return a1;
}
////////////////////////////////////////////////////////////////
function AIktra_tuqui(x1) {
  //tu qui

  var a1 = [],
    t = 0;
  for (var i = 0; i < x1.length - 3; i++) {
    if (
      x1[i].substring(4, 6) == x1[i + 1].substring(4, 6) &&
      x1[i].substring(4, 6) == x1[i + 2].substring(4, 6) &&
      x1[i].substring(4, 6) == x1[i + 3].substring(4, 6)
    ) {
      a1.push(x1[i]);
      a1.push(x1[i + 1]);
      a1.push(x1[i + 2]);
      a1.push(x1[i + 3]);
    }
  }
  return a1;
}
//////////////////////////////////////////////
function AIktra_xamco(x1) {
  //xam co
  var a1 = [],
    a2 = [];
  a2 = AIktra_tuqui(x1);

  for (var i = 0; i < x1.length - 2; i++) {
    if (
      x1[i].substring(4, 6) == x1[i + 1].substring(4, 6) &&
      x1[i].substring(4, 6) == x1[i + 2].substring(4, 6) &&
      a2.indexOf(x1[i]) < 0
    ) {
      a1.push(x1[i]);
      a1.push(x1[i + 1]);
      a1.push(x1[i + 2]);
    }
  }
  return a1;
}
//////////////////////////////////////////////////////////////
function AIktra_doithong(x1) {
  //doi thong: bao gom ket hop mang cua AIktra_doi
  var a3 = [],
    b1 = [],
    b2 = [];
  //alert(x1);
  for (var j = 0; j < x1.length; j++) {
    if (j % 2 == 0) {
      b1.push(x1[j]);
    } else {
      b2.push(x1[j]);
    }
  }

  for (var j = 0; j < b1.length - 1; j++) {
    if (
      parseInt(b1[j].substring(4, 6)) + 1 ==
      parseInt(b1[j + 1].substring(4, 6))
    ) {
      if (a3 == "") {
        a3.push(b1[j]); //3,4,5,7,8,9
        a3.push(b2[j]);
        a3.push(b1[j + 1]);
        a3.push(b2[j + 1]);
      } else {
        if (a3.indexOf(b1[j]) < 0 && a3.indexOf(b2[j]) < 0) {
          a3.push(b1[j]); //3,3,4,4,5,5,7,7
          a3.push(b2[j]);
        } else if (a3.indexOf(b1[j + 1]) < 0 && a3.indexOf(b2[j + 1]) < 0) {
          a3.push(b1[j + 1]);
          a3.push(b2[j + 1]);
        }
      }
    } else if (
      parseInt(b1[j].substring(4, 6)) + 1 !=
        parseInt(b1[j + 1].substring(4, 6)) &&
      a3.length <= 4
    ) {
      a3 = [];
    } else {
      b1.splice(j + 1, 1);
      b2.splice(j + 1, 1);
      j--;
    }
  }
  if (a3.length <= 4) {
    a3 = [];
  }

  return a3;
}

//////////////////////////////////////////////////////////////////
function AIktra_sanh(a) {
  function loc_sanh(a, b) {
    var t = -1;
    for (var i = 0; i < a.length; i++) {
      if (b.substring(4, 6) == a[i].substring(4, 6)) {
        t = i;
        break;
      }
    }
    return t;
  }
  var b = [],
    c = [],
    dem = 0,
    dem1 = 0;
  for (var i = 0; i < a.length - 1; i++) {
    if (
      parseInt(a[i].substring(4, 6)) + 1 ==
      parseInt(a[i + 1].substring(4, 6))
    ) {
      if (b == "") {
        b.push(a[i]);
        b.push(a[i + 1]);
      } else {
        if (dem == 1 && loc_sanh(b, a[i]) < 0) {
          b.push(a[i]);
          b.push(a[i + 1]);
          dem = 0;
        } else {
          b.push(a[i + 1]);
        }
      }
    } else {
      dem = 1;
    }
  }
  for (var j = 0; j < b.length - 1; j++) {
    if (
      parseInt(b[j].substring(4, 6)) + 1 ==
      parseInt(b[j + 1].substring(4, 6))
    ) {
      if (dem1 == 1) {
        c.push(b[j - 1]);

        c.push(b[j]);
        c.push(b[j + 1]);
        c = trung_lap(c);
      }

      dem1 = 1;
    } else {
      dem1 = 0;
    }
  }
  return c;
}
function AIktra_sanh_danh_sanh_loc(a, b) {
  var dem = 0,
    z = -1,
    danh = [];
  for (
    var i = 0;
    i < a.length;
    i++ //3,4,5,6  8,9,10,11
  ) {
    if (a[i].substring(4, 6) >= b[0].substring(4, 6)) {
      z = i;
      break;
    }
  }
  if (z == -1) {
    danh = [];
  } else {
    for (
      var j = z;
      j < a.length - 1;
      j++ //a[3,4,5,6,8,9,10,11]
    ) {
      if (
        parseInt(a[j].substring(4, 6)) + 1 ==
        parseInt(a[j + 1].substring(4, 6))
      ) {
        if (danh == "") {
          danh.push(a[j]);
          danh.push(a[j + 1]);
          dem += 2;
        } else {
          danh.push(a[j + 1]);
          dem++;
        }
        if (dem == b.length) {
          var t1 = danh[danh.length - 1].substring(6, 7);
          var t2 = b[b.length - 1].substring(6, 7);
          //alert(t1+"-----"+t2);
          if (t1 == "a") {
            t3 = 0.1;
          } else if (t1 == "b") {
            t1 = 0.2;
          } else if (t1 == "c") {
            t1 = 0.3;
          } else if (t1 == "d") {
            t1 = 0.4;
          }
          ///////////////////////
          if (t2 == "a") {
            t2 = 0.1;
          } else if (t2 == "b") {
            t2 = 0.2;
          } else if (t2 == "c") {
            t2 = 0.3;
          } else if (t2 == "d") {
            t2 = 0.4;
          }
          var r1 = giaomang(a, danh);
          var r2 = AIktra_sanh(r1);
          var r3 = giaomang(r1, r2);
          if (
            danh[danh.length - 1].substring(4, 6) >
              b[b.length - 1].substring(4, 6) &&
            r3 == ""
          ) {
            break;
          } else if (
            danh[danh.length - 1].substring(4, 6) ==
              b[b.length - 1].substring(4, 6) &&
            t1 > t2 &&
            r3 == ""
          ) {
            break;
          } else {
            j = z++;
            dem = 0;
            danh = [];
          }
        } else if (dem > b.length) {
          j = z;
          dem = 0;
          danh = [];
        }
      } else {
        dem = 0;
        danh = [];
      }
    }
  }
  if (danh.length < b.length) {
    danh = [];
  }
  return danh;
}
function AIktra_sanh_danh_sanh(a, b) {
  var dem = 0,
    z = -1,
    danh = [];
  if (AIktra_sanh_danh_sanh_loc(a, b) == "") {
    for (
      var i = 0;
      i < a.length;
      i++ //3,4,5,6  8,9,10,11
    ) {
      if (a[i].substring(4, 6) >= b[0].substring(4, 6)) {
        z = i;
        break;
      }
    }
    if (z == -1) {
      danh = [];
    } else {
      for (
        var j = z;
        j < a.length - 1;
        j++ //a[3,4,5,6,8,9,10,11]
      ) {
        if (
          parseInt(a[j].substring(4, 6)) + 1 ==
          parseInt(a[j + 1].substring(4, 6))
        ) {
          if (danh == "") {
            danh.push(a[j]);
            danh.push(a[j + 1]);
            dem += 2;
          } else {
            danh.push(a[j + 1]);
            dem++;
          }
          if (dem == b.length) {
            var t1 = danh[danh.length - 1].substring(6, 7);
            var t2 = b[b.length - 1].substring(6, 7);
            //alert(t1+"-----"+t2);
            if (t1 == "a") {
              t3 = 0.1;
            } else if (t1 == "b") {
              t1 = 0.2;
            } else if (t1 == "c") {
              t1 = 0.3;
            } else if (t1 == "d") {
              t1 = 0.4;
            }
            ///////////////////////
            if (t2 == "a") {
              t2 = 0.1;
            } else if (t2 == "b") {
              t2 = 0.2;
            } else if (t2 == "c") {
              t2 = 0.3;
            } else if (t2 == "d") {
              t2 = 0.4;
            }
            if (
              danh[danh.length - 1].substring(4, 6) >
              b[b.length - 1].substring(4, 6)
            ) {
              break;
            } else if (
              danh[danh.length - 1].substring(4, 6) ==
                b[b.length - 1].substring(4, 6) &&
              t1 > t2
            ) {
              break;
            } else {
              j = z;
              dem = 0;
              danh = [];
            }
          } else if (dem > b.length) {
            j = z;
            dem = 0;
            danh = [];
          }
        } else {
          dem = 0;
          danh = [];
        }
      }
    }
    if (danh.length < b.length) {
      danh = [];
    }
  } else {
    danh = AIktra_sanh_danh_sanh_loc(a, b);
  }
  return danh;
}
//////////////////////////////////////////////////////
function AI(a, x1) {
  var _danh_f = [];  
  if (a.length == 1) {
    //phong thu
    var doi = AIktra_doi(x1);
    var doi_thong = AIktra_doithong(doi);
    var tu_qui = AIktra_tuqui(x1);

    if (a[0].substring(4, 6) == "16") {
      if (doi_thong.length == 8) {
        _danh_f = doi_thong;
      } else if (tu_qui.length > 0) {
        _danh_f.push(tu_qui[0]);
        _danh_f.push(tu_qui[1]);
        _danh_f.push(tu_qui[2]);
        _danh_f.push(tu_qui[3]);
      } else if (doi_thong.length == 6) {
        _danh_f = doi_thong;
      }
    } else {
      //var cd=[];
      var c1 = giaomang(x1, doi_thong);
      var c2 = giaomang(c1, tu_qui);
      var cc = AIktra_sanh(hv_bai_lon(c2));
      var c3 = giaomang(c2, cc);

      /////////////////////////
      var doi_1 = AIktra_doi(c3);
      var c4 = giaomang(c3, doi_1);
      //alert(c4);
      if (c4 == "") {
        c4 = doi_1;
        if (c4 == "") {
          c4 = c3;
          if (c4 == "") {
            c4 = x1;
          }
        }
      }

      /////////////////////////
      _danh_f = AI_c_danh_c_1c(c4, a);
    }
  } else if (a.length == 2) {
    //phong thu
    a_rank_string = kiemtrahople(a)
    if (a_rank_string == "doi" && a[0].substring(4, 6) == "16") {
      var doi = AIktra_doi(x1);
      var doi_thong = AIktra_doithong(doi);
      var tu_qui = AIktra_tuqui(x1);

      if (doi_thong.length == 8) {
        _danh_f = doi_thong;
      } else if (tu_qui != "") {
        _danh_f = AI_loc_danh_tung_pt(tu_qui, "tuqui");
      }
    } else if (a_rank_string == "doi" && a[0].substring(4, 6) != "16") {
      _danh_f = AI_d_danh_d_2c(hoanvi_all(x1), hoanvi_all(a));
      //alert(_danh_f);
    }
  } else if (a.length == 3) {
    //phong thu
    //alert(_danh_f);
    var _danh_f = [];
    a_rank_string = kiemtrahople(a)
    if (a_rank_string == "sanh") {
      var doi1 = AIktra_doi(x1);
      var doi_thong1 = AIktra_doithong(doi1);
      var tu_qui1 = AIktra_tuqui(x1);
      var x31 = giaomang(x1, doi_thong1);
      var x32 = giaomang(x31, tu_qui1);
      var sanh1 = AIktra_sanh(hv_bai_lon(x32));
      _danh_f = AIktra_sanh_danh_sanh(sanh1, a);
    } else if (a_rank_string == "xamco" && a[0].substring(4, 6) == "16") {
      var doi = AIktra_doi(x1);
      var doi_thong = AIktra_doithong(doi);
      if (doi_thong.length == 8) {
        _danh_f = doi_thong;
      }
    } else if (a_rank_string == "xamco" && a[0].substring(4, 6) != "16") {
      var doi = AIktra_doi(x1);
      var sanh = AIktra_sanh(hv_bai_lon(x1));
      var doi_thong = AIktra_doithong(doi);
      var tu_qui = AIktra_tuqui(x1);
      var xc1 = giaomang(x1, doi_thong);
      var xc2 = giaomang(xc1, tu_qui);
      var xc3 = giaomang(xc2, sanh);

      var xam_co = AIktra_xamco(xc3);

      _danh_f = AI_xc_danh_xc_3c(xam_co, a);
    }
  } else if (a.length == 4) {
    //phong thu
    a_rank_string = kiemtrahople(a)
    if (a_rank_string == "tuqui") {
      var doi = AIktra_doi(x1);
      var doi_thong = AIktra_doithong(doi);
      var tu_qui = AIktra_tuqui(x1);
      
      if (doi_thong.length > 6) {
        _danh_f = doi_thong;
      } else if (tu_qui.length != "") {
        _danh_f = AI_tq_danh_tq_4c(tu_qui, a);
      }
    } else if (a_rank_string == "sanh") {
      var doi = AIktra_doi(x1);

      var doi_thong = AIktra_doithong(doi);
      var tu_qui = AIktra_tuqui(x1);
      var s1 = giaomang(x1, doi_thong);
      var s2 = giaomang(s1, tu_qui);
      // var s3=giaomang(s2,sanh);
      // alert(s3);
      var sanh = AIktra_sanh(hv_bai_lon(s2));
      _danh_f = AIktra_sanh_danh_sanh(sanh, a);
    }
  } else if (a.length > 4) {
    //phong thu
    a_rank_string = kiemtrahople(a)
    if (a_rank_string != "khonghople") {
      if (a_rank_string == "4doithong") {
        var doi = AIktra_doi(x1);
        var doi_thong = AIktra_doithong(doi);

        if (doi_thong.length == 8) {
          var dt = doi_thong[doi_thong.length - 1];
          var dt1 = a[a.length - 1];
          if (dt.substring(4, 6) == dt1.substring(4, 6)) {
            var dt2 = doi_thong[doi_thong.length - 1].substring(6, 7);
            var dt3 = a[a.length - 1].substring(6, 7);
            if (dt2 == "a") {
              dt2 = 0.1;
            } else if (dt2 == "b") {
              dt2 = 0.2;
            } else if (dt2 == "c") {
              dt2 = 0.3;
            } else if (dt2 == "d") {
              dt2 = 0.4;
            }
            ///////////////////////
            if (dt3 == "a") {
              dt3 = 0.1;
            } else if (dt3 == "b") {
              dt3 = 0.2;
            } else if (dt3 == "c") {
              dt3 = 0.3;
            } else if (dt3 == "d") {
              dt3 = 0.4;
            }
            if (dt2 > dt3) {
              _danh_f = doi_thong;
            }
          } else if (dt.substring(4, 6) > dt1.substring(4, 6)) {
            _danh_f = doi_thong;
          }
        } else {
          _danh_f = [];
        }
      } else if (a_rank_string == "3doithong") {
        var doi = AIktra_doi(x1);
        var doi_thong = AIktra_doithong(doi);
        var tu_qui = AIktra_tuqui(x1);

        if (doi_thong.length == 8) {
          _danh_f = doi_thong;
        } else if (tu_qui != "") {
          _danh_f = AI_loc_danh_tung_pt(tu_qui, "tuqui");
        } else if (doi_thong.length == 6) {
          var dt = doi_thong[doi_thong.length - 1];
          var dt1 = a[a.length - 1];
          if (dt.substring(4, 6) == dt1.substring(4, 6)) {
            var dt2 = doi_thong[doi_thong.length - 1].substring(6, 7);
            var dt3 = a[a.length - 1].substring(6, 7);

            if (dt2 == "a") {
              dt2 = 0.1;
            } else if (dt2 == "b") {
              dt2 = 0.2;
            } else if (dt2 == "c") {
              dt2 = 0.3;
            } else if (dt2 == "d") {
              dt2 = 0.4;
            }
            ///////////////////////
            if (dt3 == "a") {
              dt3 = 0.1;
            } else if (dt3 == "b") {
              dt3 = 0.2;
            } else if (dt3 == "c") {
              dt3 = 0.3;
            } else if (dt3 == "d") {
              dt3 = 0.4;
            }
            if (dt2 > dt3) {
              _danh_f = doi_thong;
            }
          } else if (dt.substring(4, 6) > dt1.substring(4, 6)) {
            _danh_f = doi_thong;
          }
        } else {
          _danh_f = [];
        }
      } else if (a_rank_string == "sanh") {
        //alert(sanh);
        var sanh = AIktra_sanh(hv_bai_lon(x1));
        _danh_f = AIktra_sanh_danh_sanh(sanh, a);
      }
    }
  } else if (a.length == 0) {
    //may danh:( tan cong) doi phuong bo luot
    _danh_f = AI_tancong(x1);
  }

  return _danh_f;
}

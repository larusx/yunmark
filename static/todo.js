var app = angular.module("myApp", ['ngSanitize', 'lr.upload']);
var highlight = function () {
    setTimeout(function () {
        $('pre code').each(function (i, block) {
            hljs.highlightBlock(block);
        })
    }, 1);
}

app.controller('TodoCtrl', function ($scope, $http) {
    $scope.getQueue = function () {
        $http.get('/GetQueue').success(function (data) {
            $scope.todos = data;
            $scope.oldtodos = data;
            $scope.updatetags();
            $scope.getAnnouncement();
            highlight();
        });
    };

    $scope.getAnnouncement = function () {
        $http.get('/GetAnnouncement').success(function (data) {
            $scope.announcement = data;
            highlight();
        });
    };

    $scope.addTodo = function () {
        $http.post('AddTodo', {text: $scope.todoText, tag: $scope.inputTagData}).success(function (data) {
            $scope.todos = data;
            $scope.oldtodos = data;
            $scope.updatetags();
            highlight();
        });
        $scope.todoText = '';
    };

    $scope.remaining = function () {
        var count = 0;
        angular.forEach($scope.todos, function (todo) {
            count += todo.done ? 0 : 1;
        });
        return count;
    };

    $scope.archive = function () {
        var oldTodos = $scope.oldtodos;
        var todos = $scope.todos;
        $scope.todos = [];
        angular.forEach(todos, function (todo) {
            if (todo.done) {
                for (var i = 0, max = oldTodos.length; i < max; i++) {
                    if (todo.hash == oldTodos[i].hash) {
                        oldTodos[i].done = true;
                    }
                }
            } else {
                $scope.todos.push(todo);
            }
        });
        $http.post('/SetQueue', oldTodos);
        $scope.oldtodos = [];
        angular.forEach(oldTodos, function (oldtodo) {
            if (!oldtodo.done) $scope.oldtodos.push(oldtodo);
        });
        $scope.updatetags();
        highlight();
    };

    $scope.deleteContent = function(index) {
        var op = confirm("确认删除这一条吗？")
        if(op == false)
            return;
        var hash = this.todo.hash;
        $http.post('/deleteMark', {hash: hash});
        $scope.todos.splice(index, 1);
        angular.forEach($scope.oldtodos, function(todo, idx) {
             if(todo.hash == hash) {
                 $scope.oldtodos.splice(idx, 1);
             }
        });
        $scope.updatetags();
        highlight();
    };

    $scope.modifyTodo = function () {
        var todo = this.todo;
        var index = this.$index;
        var tagsdiv = todo.hash + 1;
        var tags = [];
        $('#' + tagsdiv + ' span.tag').each(function () {
            tags.push(this.innerText);
        });

        todo.tag = tags;
        $http.post('modifyTodo', todo).success(
            function (data) {
                $scope.todos[index] = data;
                var oldtodos = $scope.oldtodos;
                for (var i = 0, max = oldtodos.length; i < max; i++) {
                    if (oldtodos[i].hash == data.hash) {
                        oldtodos[i] = data;
                        highlight();
                        return;
                    }
                }
            }
        );
        this.modify = 0;
        $scope.updatetags();
    };

    $scope.judgeTag = function () {
        if ($scope.listByTag == 'all')
            return 1;
        var tags = this.todo.tag;
        angular.forEach(tags, function (tag) {
            if (tag == $scope.listByTag)
                return 1;
        });
        return 0;
    };

    $scope.post_coding_pp = function() {
        var text = this.todo.original;
        $http.post('post_coding_pp', text).success(function (data) {
            if(data.code == 0)
                alert('已发送到Coding冒泡!');
            else if (data.code == 1000) {
                window.location.href = '/login_coding_home';
            }
        });

    };

    $scope.judgeInputStatus = function (status) {
        if (status) {
            return 'error';
        } else {
            return 'Success';
        }
    };

    $scope.judgeIfDone = function (status) {
        if (status) {
            return 'done';
        } else {
            return '';
        }
    };

    $scope.modifyContent = function () {
        this.modify = 1;
        $('.tagsinput').tagsinput();
        setTimeout(function () {
            tabIndent.renderAll();
        }, 1);
    };

    $scope.cancelModify = function () {
        this.modify = 0;
    };

    $scope.shareContent = function () {
        $http.post('shareMark', this.todo.hash);
        this.todo.shareStatus = 1;
    };

    $scope.unshareContent = function() {
        $http.post('unshareMark', this.todo.hash);
        this.todo.shareStatus = 0;
    };

    $scope.onSuccess = function (id, response) {
        var obj = $('#' + id);
        var str = obj.val();
        obj.val(str + '(' + response.data + ')');
        $scope.uploadurl = '';
    };


    $scope.onUpload = function (files) {
        $scope.uploadurl = '上传中...';
    };

    $scope.searchTags = function () {
        var tags = [];
        $("ul.select2-choices .select2-search-choice div").each(function () {
            tags.push(this.innerHTML);
        });
        if (tags.length == 0) {
            $scope.todos = $scope.oldtodos;
            return;
        }

        var todos = [];
        var oldtodos = $scope.oldtodos;
        angular.forEach(oldtodos, function (todo) {
            if ($scope.intersect(todo.tag, tags))
                todos.push(todo);
        });
        $scope.todos = todos;
        highlight();
    };

    $scope.updatetags = function () {
        var todos = $scope.oldtodos;
        var tags = {};
        for (var i = 0, maxi = todos.length; i < maxi; i++) {
            for (var j = 0, maxj = todos[i].tag.length; j < maxj; j++) {
                tags[todos[i].tag[j]] = true;
            }
        }
        $("#selectTags").empty();
        for (var tag in tags)
            $("#selectTags").append("<option value=\'" + tag + "\'>" + tag + "</option>");
    };

    $scope.intersect = function (a, b) {
        var hash = {};
        for (var i = 0, max = a.length; i < max; i++) {
            hash[a[i]] = true;
        }
        for (var i = 0, max = b.length; i < max; i++) {
            if (typeof hash[b[i]] !== "undefined")
                return true;
        }
        return false;
    };

    $scope.insertBold = function (id) {
        $('#' + id).insertAtCursor(
            '**加粗字体**'
        );
        selectTextarea(document.getElementById(id), 6, 4);
    };
    $scope.insertLink = function (id) {
        $('#' + id).insertAtCursor(
            '[链接说明](http://)'
        );
        selectTextarea(document.getElementById(id), 14, 4);
    };
    $scope.insertImage = function (id) {
        $('#' + id).insertAtCursor(
            '![图片说明](http://)'
        );
        selectTextarea(document.getElementById(id), 14, 4);
    };
    $scope.insertBullet = function (id) {
        $('#' + id).insertAtCursor(
            '- 第一条\n- 第二条'
        );
        selectTextarea(document.getElementById(id), 9, 3);
    };
    $scope.insertCode = function (id) {
        $('#' + id).insertAtCursor(
            '\n```\ncode\n```\n'
        );
        selectTextarea(document.getElementById(id), 9, 4);
    };
    $scope.insertItalic = function (id) {
        $('#' + id).insertAtCursor(
            '*倾斜字体*'
        );
        selectTextarea(document.getElementById(id), 5, 4);
    };
//    $scope.clock = new Date();
//    var updateClock = function () {
//        $scope.clock = new Date();
//    }
//    setInterval(function () {
//        $scope.$apply(updateClock);
//    }, 1000);
//    updateClock();
    $scope.getQueue();
//    $("#markdown-helo").popover(options);
    //setInterval($scope.GetQueue, 1000);
    $scope.vote = function () {
        $http.post('/vote').success(function(data) {
            if(data.code == 0)
                alert('感谢支持~');
            else if(data.code == 1) {
                if(data.msg.hasOwnProperty('html5.competition.user.not.login')) {
                    alert('请登陆Coding.net,谢谢~~');
                    window.location.href = '/login_coding_home';
                } else if(data.msg.hasOwnProperty('html5.competition.vote.repeat')) {
                    alert('感谢您的投票~~可惜只能投一次^_^');
                }
                else
                    alert(angular.toJson(data.msg));
            }
        });
    };

    $scope.get_user_list = function () {
        $http.get('/get_user_list').success(function(data) {
            $scope.user_list = data;
        });
    };

    $scope.get_user_list();

    $scope.send_mark = function(user, todo) {
        $http.post('/send_mark', {username: user, text: todo.original}).success(function(data) {
             alert('发送成功');
        });
    };

    $scope.get_receive_number = function () {
        $http.get('/get_receive_box').success(function(data) {
            $scope.unread_number = data.length;
            $scope.receive_content_list = data;
        });
    };
    $scope.get_receive_number();
    $scope.receive = function () {
        this.receiveStatus = 1;
        $scope.receive_content_list.splice(this.$index, 1);
        $scope.unread_number = $scope.unread_number - 1;
        $http.post('/AddTodo', {text: this.element.original});
        $http.post('/remove_from_receive_box', {hash: this.element.hash});
        $scope.getQueue();
    };
    $scope.delete_receive = function () {
        this.receiveStatus = 1;
        $scope.receive_content_list.splice(this.$index, 1);
        $scope.unread_number = $scope.unread_number - 1;
        $http.post('/remove_from_receive_box', {hash: this.element.hash});
    }


    $scope.expand = function () {
        this.thisStyle = '';
    }
});

app.controller('MyController', function ($scope, $interpolate) {
    // Set up a watch
    $scope.$watch('emailBody', function (body) {
        if (body) {
            var template = $interpolate(body);
            $scope.previewText =
                template({to: $scope.to});
        }
    });
});

app.controller('RegisterCtrl', function ($scope, $http) {
    $scope.register = function () {
        var password = this.password;
        if (password)
            password = hex_md5(password);
        $http.post('/register', {username: this.username, password: password}).success(function (data) {
            $scope.register_status = data;
        });
    }

    $scope.md5_this = function () {
        $scope.login_status = 1;
        var obj = $('#login-pass');
        var password = obj.val();
        obj.val(hex_md5(password));
    }

    $http.get('/GetAnnouncement').success(function (data) {
        $scope.announcement = data;
        highlight();
    });
});

app.controller('ResetCtrl', function ($scope, $http) {
    $scope.register = function () {
        var password = hex_md5($scope.password);
        $http.post('/reset_password', {username: $scope.username, password: password}).success(function (data) {
            $scope.register_status = data;
        });
    }

});
//$("#markdown-help").popover();

app.controller('ShareCtrl', function ($scope, $http) {

    $scope.username = document.getElementById('username').innerHTML;
    $scope.markShare = function() {
        $http.post('/AddTodo', {text: this.element.original, tag: "来自" + $scope.username + "的分享"});
        this.markStatus = 1;
    };
    $scope.getShare = function(username) {
        $http.post('/getShareContent', username).success(function (data) {
            $scope.shareContent = data;
            highlight();
        });
    };
    $scope.getShare($scope.username);
});

app.controller('ReceiveCtrl', function ($scope, $http) {
});
$(document).ready(function () {
    tabIndent.renderAll();
    $("select").select2({dropdownCssClass: 'dropdown-inverse'});
    $("ul.select2-choices").on('DOMSubtreeModified', function () {
        $("span.fui-search").click();
        highlight();
    });

    selectTextarea = function (textarea, cursorLeft, cursorRight) {
        var end = textarea.selectionEnd;
        var start = end - cursorLeft;
        var end = start + cursorRight;
        if (textarea.setSelectionRange) {
            textarea.setSelectionRange(parseInt(start), parseInt(end));
        } else {
            var range = textarea.createTextRange();
            range.collapse(true);
            range.moveStart('character', parseInt(start));
            range.moveEnd('character', parseInt(cursorRight));
            range.select();
        }
        textarea.focus();
    };
});
//$("table.table").on('DOMSubtreeModified', function() {
//
//});

$.fn.extend({
    insertAtCursor: function (myValue) {
        var $t = $(this)[0];
        if (document.selection) {
            this.focus();
            sel = document.selection.createRange();
            sel.text = myValue;
            this.focus();
        } else if ($t.selectionStart || $t.selectionStart == '0') {
            var startPos = $t.selectionStart;
            var endPos = $t.selectionEnd;
            var scrollTop = $t.scrollTop;
            $t.value = $t.value.substring(0, startPos) + myValue + $t.value.substring(endPos, $t.value.length);
            this.focus();
            $t.selectionStart = startPos + myValue.length;
            $t.selectionEnd = startPos + myValue.length;
            $t.scrollTop = scrollTop;
        } else {
            this.value += myValue;
            this.focus();
        }
    }
});
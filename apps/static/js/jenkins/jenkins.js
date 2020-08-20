document.write("<script type=\"text/javascript\" src=\"/static/js/layui/layui.js\"></script>");


function jobBuild(obj, job_name, arg_url, build_url, run_url, title, success_message) {
    // 执行任务
    function doBuild(parameterDict, index) {
        var parameterDict = parameterDict || {};
        requestApi({
            url: build_url,
            body: JSON.stringify(parameterDict),
            method: 'POST',
            success_message: success_message || gettext("Build success"),
            success: function () {
                if (index) {
                    layer.close(index);
                }
            },
            error: fail
        });
    }

    //渲染参数字段
    function renderFormItem(parameter) {
        // 选项类型，单选，多选，文本
        var choiceType = parameter['choiceType'] || 'ET_TEXT_BOX';
        // 选项字段名
        var name = parameter['name'];
        // 选项ID
        var randomName = parameter['randomName'];
        // 依赖字段
        var referencedParameters = parameter['referencedParameters'];
        // 字段描述
        var description = parameter['description'];
        // 字段默认值
        var defaultValue = parameter['defaultValue'];
        // 字段选项
        var choices = parameter['choices'];
        // 字段groovy脚本
        var secureScript = parameter['secureScript'];
        // 字段groovy失败后执行的脚本
        var secureFallbackScript = parameter['secureFallbackScript'];
        var parameter_el = '  <div class="layui-form-item form-group">\n';
        parameter_el += '    <label class="layui-form-label"  style="margin-right: 5px;margin-left: 50px"  title="DEFAULT_TITILE"><b>DEFAULT_NAME:</b></label>\n'.replace("DEFAULT_TITILE", description).replace("DEFAULT_NAME", name);
        parameter_el += "    <div class=\"layui-input-inline\">\n";
        if (choiceType === 'ET_TEXT_BOX') {
            var value = defaultValue || choices[0];
            parameter_el += "      <input type=\"text\" id=\"DEFAULT_ID\" name=\"DEFAULT_NAME\" value=\"DEFAULT_VALUE\" autocomplete=\"off\" class=\"layui-input form-control\" readonly>\n"
                .replace("DEFAULT_ID", randomName)
                .replace("DEFAULT_NAME", name)
                .replace("DEFAULT_VALUE", value);
            parameter_el += "    </div>\n";
        } else if (['PT_SINGLE_SELECT', 'PT_MULTI_SELECT'].includes(choiceType)) {
            if (choiceType === "PT_MULTI_SELECT") {
                parameter_el += "<select id=\"DEFAULT_ID\" name=\"DEFAULT_NAME\" class=\"form-control\" lay-verify=\"required\" multiple=\"multiple\" size=\"CHOICES_SIZE\">\n"
                    .replace("DEFAULT_ID", randomName)
                    .replace('DEFAULT_NAME', name)
                    .replace('CHOICES_SIZE', choices.length);
            } else {
                parameter_el += "<select id=\"DEFAULT_ID\" class=\"form-control\" name=\"DEFAULT_NAME\" lay-verify=\"required\">\n"
                    .replace("DEFAULT_ID", randomName)
                    .replace('DEFAULT_NAME', name);
            }

            defaultValue = defaultValue === false ? defaultValue : choices[0];

            for (var index in choices) {
                if (choices[index] == defaultValue) {
                    parameter_el += "<option value=\"DEFAULT_VALUE\" selected>DEFAULT_VALUE</option>\n"
                        .replaceAll("DEFAULT_VALUE", choices[index]);
                } else {
                    parameter_el += "<option value=\"DEFAULT_VALUE\">DEFAULT_VALUE</option>\n"
                        .replaceAll("DEFAULT_VALUE", choices[index]);
                }
            }
            parameter_el += "</select>\n";
            parameter_el += "    </div>\n";
        } else {
            console.log(choiceType);
        }
        parameter_el += "    </div>\n";
        return parameter_el
    }

    // Form表单ID
    var form_id = "parameters-form-" + job_name;

    // 获取参数成功，生成参数表单对话框，确认后执行任务
    var renderForm = function (responseJSON) {
        if (!responseJSON || !responseJSON.hasOwnProperty('args')) {
            layer.confirm(content="确认执行[<b>" + job_name + "</b>]任务构建吗?", options={icon: 3, title: '提示',shadeClose: true}, end=function (index) {
                doBuild({}, index);
            });
        } else {
            var parameters = responseJSON['args'];
            var referenceDict = responseJSON['reference'];
            var form_el = '<form class="layui-form" style="margin-top: 50px;" action="" id="DEFAULT_FORM_ID">\n'.replace("DEFAULT_FORM_ID", form_id);
            form_el += '  <div class="layui-form-item" hidden>\n';
            form_el += '    <label class="layui-form-label"><b>jenkins_job_name</b></label>\n'
            form_el += "    <div class=\"layui-input-inline\" style=\"width: 100px;\">\n";
            form_el += "      <input type=\"text\" name=\"jenkins_job_name\" value=\"DEFAULT_VALUE\" autocomplete=\"off\" class=\"layui-input\">\n".replace("DEFAULT_VALUE", job_name);
            form_el += "    </div>\n";
            form_el += "    </div>\n";

            for (var i in parameters) {
                var parameter = parameters[i];
                var parameter_el = renderFormItem(parameter);
                form_el += parameter_el;
            }
            form_el += "</form>\n";

            layer.open({
                type: 1,
                title: '<b>参数设置</b>',
                skin: 'layui-layer-molv',
                btn: [gettext('Confirm'), gettext('Cancel')],
                content: form_el,
                closeBtn: 1, // 右上角关闭按钮款式
                resize: false,
                scrollbar: false, //滚动条
                shadeClose: true, //点击遮罩关闭弹窗
                area:  '400px',
                success: function (layero, index) {
                    layui.use('form', function () {
                        var form = layui.form;
                        // 渲染表单的select项
                        form.render('select');
                        form.on('select', function (selectObj) {
                            var selectName = selectObj['elem']['name'];
                            var selectValue = selectObj['value'];
                            var scriptArgs = {}
                            scriptArgs[selectName] = selectValue;
                            //根据select项找到对应需要更改项
                            var referenceSelect = referenceDict[selectName] || [];
                            for (var item in referenceSelect) {
                                var itemName = referenceSelect[item]['name'];
                                var itemParameter = parameters[referenceSelect[item]['name']];
                                var itemId = referenceSelect[item]['id'];
                                var ele = document.getElementById(itemId);

                                requestApi({
                                    url: run_url,
                                    body: JSON.stringify({itemParameter: itemParameter, scriptArgs: scriptArgs}),
                                    method: 'POST',
                                    success_message: success_message || gettext("Run groovy script !!"),
                                    success: function (responseJSON) {
                                        ele.innerHTML = renderFormItem(responseJSON['arg_info']);
                                        form.render("select");
                                    },
                                    error: fail
                                });
                            }

                        });
                    });
                },
                //按钮1回调方法
                yes: function (index, layero) {
                    var parameterDict = $('#DEFAULT_FORM_ID'.replace("DEFAULT_FORM_ID", form_id)).serializeArray().map(function (obj, index, array) {
                        var parameter_name = obj['name'];
                        var parameter_value = obj['value'];
                        var argv = {};
                        argv[parameter_name] = parameter_value;
                        return argv
                    });
                    doBuild(parameterDict, index = index);
                }
            });
        }
    };

    // api接口请求失败
    var fail = function (responseText, responseJSON, status) {
        var errorMsg = '';
        if (responseJSON && responseJSON.error) {
            errorMsg = '';
        } else if (status === 404) {
            errorMsg = gettext("Not found")
        } else if (status === 417) {
            errorMsg = gettext("Job not found")
        } else {
            errorMsg = gettext("Server error")
        }
        swal(gettext('Error'), "[ " + job_name + " ] " + errorMsg, 'error');
    };

    var body = {}

    //请求参数列表，并渲染弹出层
    requestApi({
        url: arg_url,
        body: JSON.stringify(body),
        method: 'GET',
        success_message: success_message || gettext("Get parameters success"),
        success: renderForm,
        error: fail
    });
}

function jobBuld2(href) {
    layer.open({
        type: 2, // content是url形式
        title: ['<b>设置参数</b>', 'font-size:18px;text-align:center;'],// false 表示没标题
        // title: false,
        skin: 'layui-form',
        closeBtn: 1, // 右上角关闭按钮款式
        resize: false,
        scrollbar: false, //滚动条
        shadeClose: true, //点击遮罩关闭弹窗
        area: ["auto"],
        offset: '20%',
        content: [href, 'no'],
        success: function (layero, index) {
            layer.iframeAuto(index); //高度自适应
        },
        end: function () {
            // window.parent.location.reload();
        }
    });
}
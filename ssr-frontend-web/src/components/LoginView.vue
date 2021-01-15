<template>
	<div id="LoginView">
		<el-col :span="8" :offset="8">
			<h1>用户登录</h1>
			<el-form
				:model="LoginForm"
				status-icon :rules="rules"
				ref="LoginForm"
				label-width="100px"
				class="demo-ruleForm">
				<el-form-item label="用户名" prop="uid">
					<el-input v-model="LoginForm.uid"></el-input>
				</el-form-item>
				<el-form-item label="密码" prop="psw">
					<el-input type="password" v-model="LoginForm.psw" autocomplete="off"></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="submitForm('LoginForm')">登录</el-button>
					<el-button @click="resetForm('LoginForm')">重置</el-button>
					<el-link type="primary" style="margin-left: 15px" @click="handleReset">忘记密码？</el-link>
				</el-form-item>
			</el-form>
		</el-col>
	</div>
</template>
<script>

export default {
	data() {
		var checkUid = (rule, value, callback) => {
			if (!value) {
				return callback(new Error('用户名不能为空'));
			}
			return callback();
		};
		var validatePsw = (rule, value, callback) => {
			if (value === '') {
				return callback(new Error('请输入密码'));
			}
			return callback();
		};
		return {
			LoginForm: {
				uid: '',
				psw: '',
			},
			rules: {
				uid: [{validator: checkUid, trigger: 'blur'}],
				psw: [{validator: validatePsw, trigger: 'blur'}],
			}
		};
	},
	methods: {
		submitForm(formName) {
			this.$refs[formName].validate((valid) => {
				if (valid) {
					console.log('submit!');
					let url = process.env.VUE_APP_URL + 'users/login/';
					// let url = this.BASE_URL + 'users/login/';
					let baseModel = this.$refs[formName].model;
					let data = {
						username: baseModel.uid,
						psw: baseModel.psw,
						auth:'business',
					};
					fetch(url, {
						body: JSON.stringify(data),
						credentials: 'include',
						headers: {
							'content-type': 'application/json',
						},
						method: 'POST',
						mode: 'cors',
					})
						.then(resp => resp.json())
						.then(resp => {
							if (resp.status === 'ok') {
								this.$message({
									type: 'success',
									message: '登录成功',
									showClose: true
								});
								this.$emit('message', {
									type: 'login',
									uid: baseModel.uid,
								});
								this.$router.replace('/');
							} else {
								let reason = resp.type;
								let message;
								switch (reason) {
									case 'Already login.':
										message = '该账号已在别处登录。';
										break;
									case 'Username not exist.':
										message = '用户名不存在或密码错误。';
										break;
									case 'User has not accomplished email confirmation.':
										message = '用户尚未通过邮箱验证。';
										break;
									case 'Wrong password.':
										message = '用户名不存在或密码错误。';
										break;
									default:
										message = '未知错误。';
								}
								this.resetForm(formName);
								this.$message({
									type: 'error',
									message,
									showClose: true
								});
							}
						})
						.catch(reason => {
							console.log('reason:', reason);
							this.resetForm(formName);
							this.$message({
								type: 'error',
								message: '网络故障或服务器不可用。',
								showClose: true
							});
						});
				} else {
					// console.log('error submit!!');
					this.$message({
						type: 'warning',
						showClose: true,
						message: '您的输入不合法。'
					});
					return false;
				}
			});
		},
		resetForm(formName) {
			this.$refs[formName].resetFields();
		},
		handleReset() {
			console.log('handleReset')
			this.$prompt('请输入您的用户名，系统将会随机重置您的账号的密码，并将其发送到您的邮箱上，您随后可重新修改密码。\n您确定要重置密码吗？',
				'警告', {
					confirmButtonText: '确定',
					cancelButtonText: '取消',
					type: 'warning',
				}).then(({value}) => {
				let url = process.env.VUE_APP_URL + 'users/reset/psw/';
				// let url = this.BASE_URL + 'users/reset/psw/';
				let data = {
					username: value,
					auth:'business',
				};
				fetch(url, {
					body: JSON.stringify(data),
					credentials: 'include',
					headers: {
						'content-type': 'application/json',
					},
					method: 'POST',
					mode: 'cors',
				}).then(resp => resp.json())
					.then(resp => {
						if (resp.status === 'ok') {
							this.$notify({
								type: 'success',
								title: '重置成功',
								message: '请登录邮箱查看您的重置密码。'
							});
						} else {
							let message;
							switch (resp.type) {
								case 'Already login.':
									message = '该账号已登录，无法重置。';
									break;
								case 'Username not exist.':
									message = '用户名不存在。';
									break;
								case 'This account has not accomplished email confirmation.':
									message = '该账号尚未通过邮箱验证。';
									break;
								default:
									message = '未知错误。';
							}
							this.$notify({
								type: 'error',
								title: '重置失败',
								message,
							});
						}
					})
			}).catch(() => {
				this.$notify.info({
					title: '已取消重置',
				});
			})
		}
	},
	name: "LoginView",
}
</script>

<style scoped>
#LoginView {
	margin-top: 10%;
	text-align: center;
}
</style>
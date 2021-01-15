<template>
	<div id="RegisterView">
		<el-col :span="8" :offset="8">
			<h1>用户注册</h1>
			<el-form
				:model="RegForm"
				status-icon :rules="rules"
				ref="RegForm"
				label-width="100px">
				<el-form-item label="用户名" prop="uid">
					<el-input v-model="RegForm.uid"></el-input>
				</el-form-item>
				<el-form-item label="电子邮箱" prop="email">
					<el-input v-model="RegForm.email"></el-input>
				</el-form-item>
				<el-form-item label="密码" prop="psw1">
					<el-input type="password" v-model="RegForm.psw1" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="重复密码" prop="psw2">
					<el-input type="password" v-model="RegForm.psw2" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="submitForm('RegForm')">注册</el-button>
					<el-button @click="resetForm('RegForm')">重置</el-button>
				</el-form-item>
			</el-form>
		</el-col>
	</div>
</template>

<script>
export default {
	name: "RegisterView",
	data() {
		let checkNotEmpty = (rule, value, callback) => {
			if (value === '') {
				return callback(new Error('值不能为空'));
			}
			return callback();
		};
		let checkPsw = (rule, value, callback) => {
			if (value === '') {
				return callback(new Error('请输入密码'));
			} else {
				if (this.RegForm.psw2 !== '') {
					this.$refs.RegForm.validateField('psw2');
				}
			}
			return callback();
		};
		let checkPsw2 = (rule, value, callback) => {
			if (value === '') {
				return callback(new Error('请再次输入密码'));
			} else if (value !== this.RegForm.psw1) {
				return callback(new Error('两次密码输入不一致！'));
			}
			return callback();
		};
		return {
			RegForm: {
				uid: '',
				email: '',
				psw1: '',
				psw2: '',
			},
			rules: {
				uid: {validator: checkNotEmpty, trigger: 'blur'},
				email: {validator: checkNotEmpty, trigger: 'blur'},
				psw1: {validator: checkPsw, trigger: 'blur'},
				psw2: {validator: checkPsw2, trigger: 'blur'},
			}
		};
	},
	methods: {
		submitForm(formName) {
			this.$refs[formName].validate(valid => {
				if (valid) {
					console.log('submit!');
					let url = process.env.VUE_APP_URL + 'users/register/';
					// let url = this.BASE_URL + 'users/register/';
					let baseModel = this.$refs[formName].model;
					let data = {
						username: baseModel.uid,
						psw1: baseModel.psw1,
						psw2: baseModel.psw2,
						email: baseModel.email,
						auth: 'business',
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
									message: '注册成功',
									showClose: true,
								});
							} else {
								let reason = resp.type;
								let message;
								switch (reason) {
									case 'Invalid email address.':
										message = '邮件地址不合法。';
										break;
									case 'Username already exist.':
										message = '用户名已存在。';
										break;
									case 'Email address has been used.':
										message = '邮箱已被用于注册。';
										break;
									case 'Already login.':
										message = '该账号已在别处登录。';
										break;
									default:
										message = '未知错误。';
								}
								this.$message({
									type: 'error',
									message,
									showClose: true,
								});
							}
						})
						.catch(reason => {
							console.log('reason:', reason);
							this.$message({
								type: 'error',
								message: '网络故障或服务器不可用',
								showClose: true,
							});
						});
				} else {
					this.$message({
						type: 'warning',
						message: '您的输入不合法。',
						showClose: true,
					});
					return false;
				}
			});
		},
		resetForm(formName) {
			this.$refs[formName].resetFields();
		}
	}
}
</script>

<style scoped>
#RegisterView {
	margin-top: 10%;
}
</style>
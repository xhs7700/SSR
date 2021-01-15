<template>
	<div id="ChangePassword">
		<el-col :span="8" :offset="8">
			<h1>修改密码</h1>
			<el-form
				:model="ChangePswForm"
				status-icon :rules="rules"
				ref="ChangePswForm"
				label-width="100px">
				<el-form-item label="旧密码" prop="oldPsw">
					<el-input type="password" autocomplete="off" v-model="ChangePswForm.oldPsw"></el-input>
				</el-form-item>
				<el-form-item label="新密码" prop="newPsw">
					<el-input type="password" autocomplete="off" v-model="ChangePswForm.newPsw"></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="submitForm('ChangePswForm')">提交</el-button>
					<el-button @click="resetForm('ChangePswForm')">重置</el-button>
				</el-form-item>
			</el-form>
		</el-col>
	</div>
</template>

<script>
export default {
	name: "ChangePassword",
	data() {
		let checkOldPsw = (rule, value, callback) => {
			if (value === '') {
				return callback(new Error('请输入旧密码'));
			} else {
				if (this.ChangePswForm.newPsw !== '') {
					this.$refs.ChangePswForm.validateField('newPsw');
				}
			}
			return callback();
		}
		let checkNewPsw = (rule, value, callback) => {
			if (value === '') {
				return callback(new Error('请输入新密码'));
			} else if (value === this.ChangePswForm.oldPsw) {
				return callback(new Error('两次密码输入一致！'));
			}
			return callback();
		}
		return {
			ChangePswForm: {
				oldPsw: '',
				newPsw: '',
			},
			rules: {
				oldPsw: {validator: checkOldPsw, trigger: 'blur'},
				newPsw: {validator: checkNewPsw, trigger: 'blur'},
			}
		}
	},
	methods: {
		submitForm(formName) {
			this.$refs[formName].validate((valid) => {
				if (valid) {
					console.log('submit!');
					let url = process.env.VUE_APP_URL + 'users/set/psw/';
					// let url = this.BASE_URL + 'users/set/psw/';
					let baseModel = this.$refs[formName].model;
					let data = {
						old_password: baseModel.oldPsw,
						new_password: baseModel.newPsw,
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
									message: '修改成功',
									showClose: true,
								});
								this.$router.replace('/');
								return true;
							} else {
								let reason = resp.type;
								let message;
								switch (reason) {
									case 'Already logout.':
										message = '用户已登出。';
										break;
									case 'Invalid new password.':
										message = '用户新密码不合法。'
										break;
									case 'New password cannot be the same with old password.':
										message = '新旧密码不能相同。';
										break;
									case 'Wrong password.':
										message = '密码错误。';
										break;
									default:
										message = '未知错误。';
								}
								this.$message({
									type: 'error',
									message,
									showClose: true,
								});
								return false;
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
							return false;
						})
				} else {
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
		}
	}
}
</script>

<style scoped>

</style>
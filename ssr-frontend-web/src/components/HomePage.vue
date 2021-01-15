<template>
	<div id="HomePage">
		<el-menu
			class="el-menu-demo"
			mode="horizontal"
			@select="handleSelect">
			<el-menu-item index="home" v-show="HomePageData.isLogin">
				<i class="el-icon-house"></i>
				<span slot="title">主页</span>
			</el-menu-item>
			<el-menu-item index="login" v-show="!HomePageData.isLogin">
				<i class="el-icon-unlock"></i>
				<span slot="title">登录</span>
			</el-menu-item>
			<el-menu-item index="register" v-show="!HomePageData.isLogin">
				<i class="el-icon-edit-outline"></i>
				<span slot="title">注册</span>
			</el-menu-item>
			<el-submenu index="user" v-show="HomePageData.isLogin">
				<template slot="title">
					<i class="el-icon-user"></i>
					<span>用户</span>
				</template>
				<el-menu-item-group>
					<el-menu-item index="user_info" disabled>用户名：{{ this.HomePageData.uid }}</el-menu-item>
					<el-menu-item index="change_psw">修改密码</el-menu-item>
				</el-menu-item-group>
			</el-submenu>
			<el-menu-item index="logout" v-show="HomePageData.isLogin">
				<i class="el-icon-lock"></i>
				<span slot="title">登出</span>
			</el-menu-item>
		</el-menu>
		<router-view @message="handleMessage" :HomePageData="HomePageData"></router-view>
	</div>
</template>

<script>
export default {
	name: "HomePage",
	data() {
		return {
			HomePageData: {
				isLogin: false,
				uid: null,
			},
		}
	},
	mounted() {
		let url = `${process.env.VUE_APP_URL}users/get/user/`;
		fetch(url, {
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
					this.HomePageData.uid = resp.content.username;
					this.HomePageData.isLogin = true;
				} else {
					this.HomePageData.uid = null;
					this.HomePageData.isLogin = false;
				}
			})
			.catch(reason => {
				console.log('fail to get current user.')
				console.log('reason:', reason);
			});
	},
	methods: {
		handleLogout() {
			let url = process.env.VUE_APP_URL + 'users/logout/';
			// let url = this.BASE_URL + 'users/logout/';
			fetch(url, {
				credentials: 'include',
				headers: {
					'content-type': 'application/json',
				},
				method: 'POST',
				mode: 'cors',
			})
				.then(resp => resp.json())
				.then(resp => {
					this.HomePageData.uid = null;
					this.HomePageData.isLogin = false;
					if (resp.status === 'ok') {
						this.$message({
							type: 'success',
							message: '登出成功。',
							showClose: true,
						});
					} else {
						this.$message({
							type: 'error',
							message: '用户已登出',
							showClose: true,
						});
					}
				})
				.catch(reason => {
					console.log('reason:', reason);
					this.$message({
						type: 'error',
						message: '网络故障或服务器不可用。',
						showClose: true
					});
				});
		},
		handleSelect(key, keyPath) {
			console.log('key:', key, keyPath);
			let route;
			switch (key) {
				case 'home':
					route = '/';
					break;
				case 'logout':
					this.handleLogout();
					route = '/'
					break;
				default:
					route = key;
			}
			console.log('route:', route);
			this.$router.push(route);
		},
		handleMessage(message) {
			// console.log(message);
			switch (message.type) {
				case 'login':
					this.HomePageData.isLogin = true;
					this.HomePageData.uid = message.uid;
					break;
				default:
					break;
			}
		}
	}
}
</script>

<style scoped>
#HomePage {
	font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}
</style>
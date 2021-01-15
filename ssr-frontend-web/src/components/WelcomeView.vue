<template>
	<div id="WelcomeView">
		<el-container v-if="HomePageData.isLogin">
			<el-aside width="200px">
				<el-menu
					@open="handleOpen"
					@close="handleClose">
					<el-menu-item @click="handleClick" index="region">
						<i class="el-icon-location-outline"></i>
						<span slot="title">地点</span>
					</el-menu-item>
					<el-menu-item @click="handleClick" index="device">
						<i class="el-icon-monitor"></i>
						<span slot="title">设备</span>
					</el-menu-item>
					<el-menu-item @click="handleClick" index="order">
						<i class="el-icon-message"></i>
						<span slot="title">工单</span>
					</el-menu-item>
					<el-menu-item @click="handleClick" index="income">
						<i class="el-icon-data-line"></i>
						<span slot="title">营收</span>
					</el-menu-item>
				</el-menu>
			</el-aside>
			<el-main>
				<router-view v-if="HomePageData.isLogin" :HomePageData="HomePageData"></router-view>
			</el-main>
		</el-container>
		<div class="not-login" v-if="!HomePageData.isLogin">
			<div id="not-login-SSRD">SSR-Dashboard</div>
			<div id="not-login—SSR">Shared Shower Room</div>
		</div>
	</div>
</template>

<script>
export default {
	name: "WelcomeView",
	props: ['HomePageData'],
	watch: {
		HomePageData: function (val) {
			this.HomePageData = val;
		}
	},
	methods: {
		handleOpen(key, keyPath) {
			console.log('key:', key, keyPath);
		},
		handleClose(key, keyPath) {
			console.log('key:', key, keyPath);
		},
		handleClick(key, keyPath) {
			console.log('key:', key, keyPath);
			console.log('key.index:', key.index);
			this.$router.push(key.index);
		}
	},
}
</script>

<style scoped>
.not-login {
	margin-top: 20%;
}

#not-login-SSRD {
	font-size: xxx-large;
}

#not-login—SSR {
	font-size: xx-large;
}
</style>

import Vue from 'vue'
import VueRouter from "vue-router";
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css'

import HomePage from "@/components/HomePage";
import LoginView from "@/components/LoginView";
import RegisterView from "@/components/RegisterView";
import WelcomeView from "@/components/WelcomeView";
import ChangePassword from "@/components/ChangePassword";
import RegionBoard from "@/components/RegionBoard";
import DeviceBoard from "@/components/DeviceBoard";
import OrderBoard from "@/components/OrderBoard";
import IncomeBoard from "@/components/IncomeBoard";

Vue.use(ElementUI);
Vue.use(VueRouter);

Vue.config.productionTip = false;

Vue.config.productionTip = false

const routes = [
	{
		path: '/',
		component: HomePage,
		children: [
			{
				path: 'login',
				component: LoginView,
			},
			{
				path: 'register',
				component: RegisterView,
			},
			{
				path: '',
				component: WelcomeView,
				children: [
					{
						path: 'region',
						component: RegionBoard,
					},
					{
						path: 'device',
						component: DeviceBoard,
					},
					{
						path: 'order',
						component: OrderBoard,
					},
					{
						path: 'income',
						component: IncomeBoard,
					}
				]
			},
			{
				path: 'change_psw',
				component: ChangePassword,
			},
		]
	},
]

const router = new VueRouter({
	mode: 'history',
	routes,
})

new Vue({
	router,
	render: h => h(App),
}).$mount('#app')

<template>
	<div id="OrderBoard">
		<el-table :data="OrderData" stripe style="width: 100%">
			<el-table-column
				prop="device"
				label="设备名"
				:filters="$data.filterDevice"
				:filter-method="filterHandler"
				sortable>
				<template slot-scope="scope">
					<i class="el-icon-monitor"></i>
					<span style="margin-left: 10px">{{ scope.row.device }}</span>
				</template>
			</el-table-column>
			<el-table-column
				prop="type"
				label="工单类型"
				:filters="[
					{text:'物理损坏',value:'物理损坏'},
					{text:'无法启动',value:'无法启动'},
					{text:'无法进出',value:'无法进出'},
					{text:'其他原因',value:'其他原因'},
				]"
				:filter-method="filterHandler"
				sortable>
				<template slot-scope="scope">
					<span>{{ scope.row.type }}</span>
				</template>
			</el-table-column>
			<el-table-column
				prop="synopsis"
				label="描述">
				<template slot-scope="scope">
					<el-popover trigger="hover" placement="top">
						<p>完整描述：{{ scope.row.description }}</p>
						<div slot="reference" class="synopsis-wrapper">
							<el-tag size="medium">{{ scope.row.synopsis }}</el-tag>
						</div>
					</el-popover>
				</template>
			</el-table-column>
		</el-table>
	</div>
</template>

<script>
export default {
	name: "OrderBoard",
	data() {
		let url = process.env.VUE_APP_URL + 'users/get/order/';
		// let url = this.BASE_URL + 'users/get/order/';
		let ans = {OrderData: []};
		let deviceSet = new Set();
		fetch(url, {
			credentials: 'include',
			headers: {
				'content-type': 'application/json',
			},
			method: 'GET',
			mode: 'cors',
		})
			.then(resp => resp.json())
			.then(resp => {
				if (resp.status === 'ok') {
					console.log(resp);
					ans.OrderData = resp.content;
					for (let order of ans.OrderData) {
						if (!deviceSet.has(order.device)) {
							deviceSet.add(order.device);
						}
						order.synopsis = order.description.substring(0, 50);
					}
					// ans.filterDevice=Array.from(deviceSet);
					ans.filterDevice = [];
					deviceSet.forEach(device => ans.filterDevice.push({text: device, value: device}));
					console.log(ans.OrderData);
				} else {
					let reason = resp.type;
					let message;
					switch (reason) {
						case 'Already logout.':
							message = '用户已登出。';
							break;
						default:
							message = '未知错误。'
					}
					this.$message({
						type: 'error',
						message,
						showClose: true
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
		return ans;
	},
	methods: {
		filterHandler(value, row, column) {
			const property = column['property'];
			return row[property] === value;
		},
	},
}
</script>

<style scoped>

</style>
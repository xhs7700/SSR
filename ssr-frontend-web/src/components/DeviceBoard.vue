<template>
	<div id="DeviceBoard">
		<el-table :data="DeviceData" stripe style="width: 100%">
			<el-table-column
				prop="name"
				label="设备名"
				sortable>
				<template slot-scope="scope">
					<i class="el-icon-monitor"></i>
					<span style="margin-left: 10px">{{ scope.row.name }}</span>
				</template>
			</el-table-column>
			<el-table-column
				prop="location"
				label="地点"
				:filters="$data.filterRegion"
				:filter-method="filterHandler"
				sortable>
				<template slot-scope="scope">
					<i class="el-icon-place"></i>
					<span style="margin-left: 10px">{{ scope.row.location }}</span>
				</template>
			</el-table-column>
			<el-table-column
				prop="status"
				label="状态"
				:filters="[{text:'在线',value:'在线'},{text:'离线',value:'离线'},{text:'故障',value:'故障'},]"
				:filter-method="filterHandler"
				sortable>
				<template slot-scope="scope">
					<i :class="getStatusIcon(scope.row.status)"></i>
					<span style="margin-left: 10px">{{ scope.row.status }}</span>
				</template>
			</el-table-column>
			<el-table-column>
				<template slot="header">
					<span>操作</span>
					<el-button
						type="primary"
						icon="el-icon-plus"
						round
						style="margin-left: 5px"
						size="mini"
						@click="handleAdd">新增
					</el-button>
					<el-button
						type="success"
						icon="el-icon-download"
						round
						style="margin-left: 5px"
						size="mini"
						@click="handleDownload('SSR-设备数据.csv')">导出
					</el-button>
				</template>
				<template slot-scope="scope">
					<el-button
						size="mini"
						icon="el-icon-edit"
						@click="handleEdit(scope.$index,scope.row)">编辑
					</el-button>
					<el-button
						size="mini"
						type="danger"
						icon="el-icon-delete"
						@click="handleDelete(scope.$index,scope.row)">删除
					</el-button>
				</template>
			</el-table-column>
		</el-table>
		<el-dialog title="设备" :visible.sync="dialogFormVisible">
			<el-form :model="form" ref="form">
				<el-form-item
					prop="name"
					:rules="[{required:true,message:'设备名不能为空'}]"
					label="设备名">
					<el-input v-model="form.name" autocomplete="off"></el-input>
				</el-form-item>
				<el-form-item
					prop="location"
					label="地点">
					<el-select v-model="form.location" placeholder="请选择地点" filterable>
						<el-option
							v-for="item in $data.optionRegion"
							:key="item.value"
							:label="item.label"
							:value="item.value">
						</el-option>
					</el-select>
				</el-form-item>
				<el-form-item
					prop="status"
					label="状态">
					<el-select v-model="form.status" placeholder="请选择状态">
						<el-option
							v-for="item in $data.optionStatus"
							:key="item.value"
							:label="item.label"
							:value="item.value">
						</el-option>
					</el-select>
				</el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click="dialogFormVisible=false">取消</el-button>
				<el-button type="primary" @click="submitForm('form')">确定</el-button>
			</div>
		</el-dialog>
	</div>
</template>

<script>
export default {
	name: "DeviceBoard",
	data() {
		let url = process.env.VUE_APP_URL + 'users/get/device/';
		// let url = this.BASE_URL + 'users/get/device/';
		let ans = {DeviceData: []};
		// ans.DeviceData=myFetch(url);
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
					ans.DeviceData = resp.content;
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
		url = process.env.VUE_APP_URL + 'users/get/place/'
		// url = this.BASE_URL + 'users/get/place/'
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
					console.log('RegionResp:', resp);
					ans.optionRegion = resp.content.map(region => {
						return {
							label: region.name,
							value: region.name,
						};
					});
					ans.filterRegion = resp.content.map(region => {
						return {
							text: region.name,
							value: region.name,
						};
					});
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
		ans.dialogFormVisible = false;
		ans.formLabelWidth = '120px';
		ans.setTable = {
			index: null,
			row: null,
			type: null,
		};
		ans.optionStatus = [
			{value: '在线', label: '在线'},
			{value: '离线', label: '离线'},
			{value: '故障', label: '故障'},
		]
		ans.form = {
			status: '',
			location: '',
			name: '',
		};
		return ans;
	},
	methods: {
		getStatusIcon(status) {
			switch (status) {
				case '故障':
					return 'el-icon-warning';
				case '在线':
					return 'el-icon-circle-check';
				case '离线':
					return 'el-icon-circle-close';
				default:
					return 'el-icon-question';
			}
		},
		filterHandler(value, row, column) {
			const property = column['property'];
			return row[property] === value;
		},
		handleAdd() {
			this.setTable.type = 'add';
			this.dialogFormVisible = true;
		},
		handleEdit(index, row) {
			console.log(index, row);
			this.setTable = {
				index: index,
				row: row,
				type: 'edit',
			}
			this.form.status = row.status;
			this.form.location = row.location;
			this.form.name = row.name;
			this.dialogFormVisible = true;
		},
		fake_click(obj) {
			let ev = document.createEvent('MouseEvent');
			ev.initMouseEvent('click', true, false, window,
				0, 0, 0, 0, 0, false, false, false, false, 0, null);
			obj.dispatchEvent(ev);
		},
		getData() {
			let lines = ['设备名,地点,状态'];
			for (let device of this.DeviceData.values()) {
				let line = `${device.name},${device.location},${device.status}`;
				lines.push(line);
			}
			return lines.join('\n');
		},
		handleDownload(name) {
			let urlObject = window.URL || window.webkitURL || window;
			let data = this.getData();
			let downloadData = new Blob(['\ufeff' + data], {type: 'text/csv'});
			let save_link = document.createElementNS('http://www.w3.org/1999/xhtml', 'a');
			save_link.href = urlObject.createObjectURL(downloadData);
			save_link.download = name;
			this.fake_click(save_link);
		},
		handleDelete(index, row) {
			console.log(index, row);
			let url = process.env.VUE_APP_URL + 'users/delete/device/';
			// let url = this.BASE_URL + 'users/delete/device/';
			let request_data = {
				loc_name: row.location,
				dev_name: row.name,
			};
			fetch(url, {
				body: JSON.stringify(request_data),
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
							message: '删除成功',
							showClose: true,
						});
						let idx = this.DeviceData.indexOf(row);
						this.DeviceData.splice(idx, 1);
					} else {
						this.$message({
							type: 'error',
							message: resp.type,
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
		},
		submitForm(formName) {
			this.$refs[formName].validate(valid => {
				if (valid) {
					let data = this.setTable;
					let baseModel = this.$refs[formName].model;
					let url;
					let request_data = {
						status: baseModel.status,
						loc_name: baseModel.location,
						dev_name: baseModel.name,
					};
					if (data.type === 'edit') {
						url = process.env.VUE_APP_URL + 'users/set/device/';
						// url = this.BASE_URL + 'users/set/device/';
						request_data.loc_name_old = data.row.location;
						request_data.dev_name_old = data.row.name;
					} else {
						url = process.env.VUE_APP_URL + 'users/add/device/';
						// url = this.BASE_URL + 'users/add/device/';
					}
					fetch(url, {
						body: JSON.stringify(request_data),
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
							} else {
								this.$message({
									type: 'error',
									message: resp.type,
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
					if (data.type === 'edit') {
						data.row.name = baseModel.name;
						data.row.location = baseModel.location;
						data.row.status = baseModel.status;
					} else {
						this.DeviceData.push({
							status: baseModel.status,
							location: baseModel.location,
							name: baseModel.name,
						});
					}
				} else {
					this.$message({
						type: 'warning',
						message: '您的输入不合法。',
						showClose: true,
					});
				}
			});
			this.dialogFormVisible = false;
		}
	},
}
</script>

<style scoped>

</style>
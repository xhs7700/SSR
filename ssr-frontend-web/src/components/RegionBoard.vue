<template>
	<div id="RegionBoard">
		<el-table :data="RegionData" stripe style="width: 100%">
			<el-table-column
				prop="name"
				label="地名"
				sortable>
				<template slot-scope="scope">
					<i class="el-icon-place"></i>
					<span style="margin-left: 10px">{{ scope.row.name }}</span>
				</template>
			</el-table-column>
			<el-table-column
				prop="longitude"
				label="经度"
				sortable>
				<template slot-scope="scope">
					<span>{{ scope.row.longitude }}</span>
				</template>
			</el-table-column>
			<el-table-column
				prop="latitude"
				label="纬度"
				sortable>
				<template slot-scope="scope">
					<span>{{ scope.row.latitude }}</span>
				</template>
			</el-table-column>
			<el-table-column>
				<template slot="header">
					<span>操作</span>
					<el-button
						type="primary"
						icon="el-icon-plus"
						round
						style="margin-left: 15px"
						size="mini"
						@click="handleAdd">新增
					</el-button>
					<el-button
						type="success"
						icon="el-icon-download"
						round
						style="margin-left: 15px"
						size="mini"
						@click="handleDownload('SSR-地点数据.csv')">导出
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
		<el-dialog title="地点" :visible.sync="dialogFormVisible">
			<el-form :model="form" ref="form">
				<el-form-item
					prop="name"
					:rules="[{required:true,message:'地名不能为空'}]"
					label="地名">
					<el-input v-model="form.name" autocomplete="off"></el-input>
				</el-form-item>
				<el-form-item
					prop="longitude"
					:rules="[
						{required: true,message: '经度不能为空'},
						{type:'number',message: '经度必须为数字'}
					]"
					label="经度">
					<el-input v-model.number="form.longitude" autocomplete="off"></el-input>
				</el-form-item>
				<el-form-item
					prop="latitude"
					:rules="[
						{required: true,message: '纬度不能为空'},
						{type:'number',message: '纬度必须为数字'}
					]"
					label="纬度">
					<el-input v-model.number="form.latitude" autocomplete="off"></el-input>
				</el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click="dialogFormVisible = false">取消</el-button>
				<el-button type="primary" @click="submitForm('form')">确定</el-button>
			</div>
		</el-dialog>
	</div>
</template>

<script>
export default {
	name: "RegionBoard",
	// props:['HomePageData'],
	// watch:{
	// 	HomePageData:function (val) {
	// 		this.HomePageData=val;
	// 	}
	// },
	data() {
		let url = process.env.VUE_APP_URL + 'users/get/place/';
		// let url = this.BASE_URL + 'users/get/place/';
		let ans = {RegionData: []};
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
					ans.RegionData = resp.content;
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
		}
		ans.form = {
			longitude: '',
			latitude: '',
			name: '',
		}
		return ans;
	},
	methods: {
		handleEdit(index, row) {
			this.setTable = {
				index: index,
				row: row,
				type: 'edit'
			}
			this.form.name = row.name;
			this.form.longitude = row.longitude;
			this.form.latitude = row.latitude;
			this.dialogFormVisible = true;
		},
		handleAdd() {
			this.setTable.type = 'add';
			this.dialogFormVisible = true;
		},
		fake_click(obj) {
			let ev = document.createEvent('MouseEvent');
			ev.initMouseEvent('click', true, false, window,
				0, 0, 0, 0, 0, false, false, false, false, 0, null);
			obj.dispatchEvent(ev);
		},
		getData() {
			let lines = ['地名,经度,纬度'];
			for (let region of this.RegionData.values()) {
				let line = `${region.name},${region.longitude},${region.latitude}`;
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
			let url = process.env.VUE_APP_URL + 'users/delete/place/';
			// let url = this.BASE_URL + 'users/delete/place/';
			let request_data = {name: row.name}
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
						let idx = this.RegionData.indexOf(row);
						this.RegionData.splice(idx, 1);
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
						longitude: baseModel.longitude,
						latitude: baseModel.latitude,
					};
					if (data.type === 'edit') {
						url = process.env.VUE_APP_URL + 'users/set/place/';
						// url = this.BASE_URL + 'users/set/place/';
						request_data.old_name = data.row.name;
						request_data.new_name = baseModel.name;
					} else {
						url = process.env.VUE_APP_URL + 'users/add/place/';
						// url = this.BASE_URL + 'users/add/place/';
						request_data.name = baseModel.name;
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
						data.row.longitude = baseModel.longitude;
						data.row.latitude = baseModel.latitude;
					} else {
						this.RegionData.push(request_data);
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
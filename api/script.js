const axios = require("axios");
const fs = require("fs");

// specify number of revisions
var rvlimit = 500;

// url parameters
let url = "https://en.wikipedia.org/w/api.php";
let params = {
	action: "query",
	prop: "revisions",
	titles: "",
	rvlimit: rvlimit,
	rvprop: "ids|flags|user|userid|timestamp|size|comment|content|tags",
	rvslots: "main",
	formatversion: "2",
	format: "json",
};

async function getRevisions(url, params) {
	console.log("Making Request...", params.titles);
	let response = await axios.get(url, { params: params });
	let data = response.data;
	return data;
}

async function fetchRevisions(title, data) {
	console.log("Fetching data...", title);
	params.titles = title;
	let result = await getRevisions(url, params);
	// console.log(data.query);
	if (!data.title) {
		data.title = result.query.pages[0].title;
		data.pageId = result.query.pages[0].pageid;
	}
	for (const revision of result.query.pages[0].revisions) {
		let revision_data = {};
		revision_data.revId = revision.revid;
		revision_data.parentId = revision.parentid;
		revision_data.flags = revision.flags;
		revision_data.user = revision.user;
		revision_data.userid = revision.userid;
		revision_data.timestamp = revision.timestamp;
		revision_data.size = revision.size;
		revision_data.comment = revision.comment;
		const vandal_regex = new RegExp("vandal", "i");
		const minor_regex = new RegExp("minor", "i");
		const revert_regex = new RegExp("revert", "i");
		revision_data.minor = minor_regex.test(revision.comment);
		revision_data.vandal = vandal_regex.test(revision.comment);
		revision_data.revert = revert_regex.test(revision.comment);
		revision_data.content = revision["slots"]["main"]["content"];
		data.revisions.push(revision_data);
	}
	if (data.continue && revisions.length < rvlimit) {
		params.rvcontinue = data.continue.rvcontinue;
		await fetchRevisions(title, data);
	} else {
		return data;
	}
}

function readFiles(file1, file2) {
	return new Promise((resolve, reject) => {
		fs.readFile(file1, "utf8", (err, data1) => {
			if (err) reject(err);
			fs.readFile(file2, "utf8", (err, data2) => {
				if (err) reject(err);
				resolve({ data1, data2 });
			});
		});
	});
}

function replaceNonAscii(text) {
	// Replace non-ASCII characters with closest ASCII equivalents
	return text.replace(/[^\x00-\x7F]/g, function (match) {
		return match.normalize("NFKD").replace(/[^\w\s-]/g, "");
	});
}

function cleanTitle(text) {
	// Replace non-ASCII characters with closest ASCII equivalents
	let asciiText = text.normalize("NFKD").replace(/[^\x00-\x7F]/g, "");

	// Replace dashes, dots, and apostrophes with underscores (zipping causes issues with dashes, spaces, dots etc. in file names)
	let replacedText = asciiText.replace(/[-.'\s']/g, "_");

	return replacedText;
}

//  Reading files and fetching revisions

readFiles("Controversial_topics.json", "Noncontroversial_topics.json")
	.then(({ data1, data2 }) => {
		var ARTICLE_NAMES_CONTROVERSIAL = JSON.parse(data1);
		var ARTICLE_NAMES_NON_CONTOVERSIAL = JSON.parse(data2);
		ARTICLE_NAMES_CONTROVERSIAL = ARTICLE_NAMES_CONTROVERSIAL.slice(0, 0);
		ARTICLE_NAMES_NON_CONTOVERSIAL = ARTICLE_NAMES_NON_CONTOVERSIAL.slice(300, 400);
		ARTICLE_NAMES_CONTROVERSIAL.forEach(title => {
			var data = { title: "", pageId: "", revisions: [] };
			fetchRevisions(title, data)
				.then(async () => {
					fs.writeFile(
						`controversial_dataset/${cleanTitle(title)}.json`,
						replaceNonAscii(JSON.stringify(data)),
						"utf8",
						err => {
							if (err) throw err;
							console.log(
								`The file controversial_dataset/${cleanTitle(
									title,
								)}.json has been saved!`,
							);
						},
					);
					// await timeout of 5seconds
					await new Promise(resolve => setTimeout(resolve, 5000)).then(() => {});
				})
				.catch(error => {
					console.error(error);
				});
		});
		ARTICLE_NAMES_NON_CONTOVERSIAL.forEach(title => {
			var data = { title: "", pageId: "", revisions: [] };
			fetchRevisions(title, data)
				.then(async () => {
					fs.writeFile(
						`noncontroversial_dataset/${cleanTitle(title)}.json`, // cleaning the title and body to remove non ascii characters
						replaceNonAscii(JSON.stringify(data)),
						"utf8",
						err => {
							if (err) throw err;
							console.log(
								`The file noncontroversial_dataset/${cleanTitle(
									title,
								)}.json has been saved!`,
							);
						},
					);
					await new Promise(resolve => setTimeout(resolve, 5000)).then(() => {});
				})
				.catch(error => {
					console.error(error);
				});
		});
	})
	.catch(err => {
		console.log(err);
	});

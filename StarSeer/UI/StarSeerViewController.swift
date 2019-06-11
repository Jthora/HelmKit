//
//  StarSeerViewController.swift
//  HelmKit
//
//  Created by Jordan Trana on 6/5/19.
//  Copyright © 2019 Jordan Trana. All rights reserved.
//

import UIKit
import SpriteKit

class StarSeerViewController: UIViewController {

    @IBOutlet weak var starChartView: UIView!
    @IBOutlet weak var timeSpeedSubView: UIView!
    @IBOutlet weak var timeOffsetSubView: UIView!
    
    @IBOutlet weak var starChartSpriteKitView: SKView!
    @IBOutlet var starChartTapGestureRecognizer: UITapGestureRecognizer!
    @IBOutlet weak var starChartHeightConstraint: NSLayoutConstraint!
    var starChartHeight:CGFloat {
        get {
            return starChartHeightConstraint.constant
        }
        set {
            self.starChartHeightConstraint.constant = newValue
        }
    }
    
    @IBOutlet weak var timeSpeedLabel: UILabel!
    @IBOutlet weak var timeOffsetLabel: UILabel!
    
    @IBOutlet var timeSpeedPanGestureRecognizer: UIPanGestureRecognizer!
    @IBOutlet var timeOffsetPanGestureRecognizer: UIPanGestureRecognizer!
    
    @IBOutlet weak var trackerDateLabel: UILabel!
    
    var updateTimer:Timer = Timer.scheduledTimer(withTimeInterval: 1.0/60.0, repeats: true) { (timer) in
        DispatchQueue.main.async {
            StarSeerViewController.`$`?.update()
        }
    }
    var currentDate:Date = Date()
    var scrubberDate:Date = Date()
    var lastScrubberTimeOffset:TimeInterval = 0
    
    var timeSpeedScrubberController: TimeSpeedScrubberSubViewController? = nil
    var timeOffsetScrubberController: TimeOffsetScrubberSubViewController? = nil
    var starChartController: StarChartSubViewController? = nil
    
    static weak var `$`:StarSeerViewController? = nil
    
    override func viewDidLoad() {
        super.viewDidLoad()
        StarSeerViewController.`$` = self

        timeSpeedScrubberController = TimeSpeedScrubberSubViewController(wideNarrowContainerView: timeSpeedSubView, timeSpeedLabel: timeSpeedLabel, panGestureRecognizer: timeSpeedPanGestureRecognizer)
        timeOffsetScrubberController = TimeOffsetScrubberSubViewController(wideNarrowContainerView: timeOffsetSubView, timeOffsetLabel: timeOffsetLabel, panGestureRecognizer: timeOffsetPanGestureRecognizer)
        starChartController = StarChartSubViewController(wideNarrowContainerView: starChartView, wideNarrowSpriteKitView: starChartSpriteKitView)
        
        
    }
    
    func update() {
        let newDate = Date()
        let dateDelta = abs(currentDate.timeIntervalSince(newDate))
        currentDate = newDate
        
        let dateDeltaWarped = dateDelta * TimeInterval(timeSpeedScrubberController?.warp ?? 1)
        scrubberDate = scrubberDate.addingTimeInterval(dateDeltaWarped)
        
        timeOffsetScrubberController?.timeOffset += dateDeltaWarped - dateDelta
        let dateOffsetDelta = TimeInterval(timeOffsetScrubberController?.timeOffset ?? 0) - lastScrubberTimeOffset
        lastScrubberTimeOffset = timeOffsetScrubberController?.timeOffset ?? 0
        
        scrubberDate = scrubberDate.addingTimeInterval(dateOffsetDelta)
        
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .medium
        dateFormatter.timeStyle = .medium
        trackerDateLabel.text = dateFormatter.string(from: scrubberDate)
    }

    @IBAction func timeSpeedGestureRecognizer(_ sender: UIPanGestureRecognizer) {
        timeSpeedScrubberController?.timeSpeedGestureRecognizer(sender)
    }
    
    @IBAction func timeOffsetGestureRecognizer(_ sender: UIPanGestureRecognizer) {
        timeOffsetScrubberController?.timeOffsetGestureRecognizer(sender)
    }
    
    @IBAction func timeSpeedDoubleTapGestureRecognizer(_ sender: Any) {
        timeSpeedScrubberController?.timeSpeed = 1
    }
    
    @IBAction func timeOffsetDoubleTapGestureRecognizer(_ sender: Any) {
        timeOffsetScrubberController?.timeOffset = 0
        lastScrubberTimeOffset = 0
        scrubberDate = currentDate
    }
    
    @IBAction func timeSpeedSingleTapGestureRecognizer(_ sender: Any) {
        timeSpeedScrubberController?.toggleFold()
    }
    
    @IBAction func timeOffsetSingleTapGestureRecognizer(_ sender: Any) {
        timeOffsetScrubberController?.toggleScale()
    }
    @IBAction func starChartTapGestureRecognizer(_ sender: UITapGestureRecognizer) {
        if starChartHeight == view.bounds.height * 0.4 {
            UIView.animate(withDuration: 0.5) {
                self.starChartHeight = self.view.bounds.height
            }
        } else if starChartHeight == view.bounds.height {
            UIView.animate(withDuration: 0.5) {
                self.starChartHeight = self.view.bounds.height * 0.4
            }
        }
    }
    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
